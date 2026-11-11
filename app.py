
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

from backend.predictor import predict_machine_failure

from database.db_operations import (
    initialize_database,
    save_prediction_with_alert,
    get_machines as db_get_machines,
    get_machine,
    get_predictions as db_get_predictions,
    get_alerts as db_get_alerts,
    resolve_alert
)


app = Flask(__name__)
CORS(app)

# Frontend directory
PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


# Initialize database
initialize_database()


# --------------------------------------------------
# DEMONSTRATION MACHINE PROFILES
# --------------------------------------------------

MACHINE_PROFILES = [
    {
        "machine_id": "MCH-001",
        "name": "Electric Motor",
        "machine_type": "L",
        "air_temperature": 298.1,
        "process_temperature": 308.6,
        "rotational_speed": 1500,
        "torque": 40,
        "tool_wear": 20,
        "status": "Healthy"
    },
    {
        "machine_id": "MCH-002",
        "name": "Centrifugal Pump",
        "machine_type": "M",
        "air_temperature": 299.5,
        "process_temperature": 310.2,
        "rotational_speed": 1450,
        "torque": 42,
        "tool_wear": 85,
        "status": "Healthy"
    },
    {
        "machine_id": "MCH-003",
        "name": "Industrial Gearbox",
        "machine_type": "H",
        "air_temperature": 301.2,
        "process_temperature": 312.5,
        "rotational_speed": 1380,
        "torque": 48,
        "tool_wear": 145,
        "status": "At Risk"
    },
    {
        "machine_id": "MCH-004",
        "name": "Air Compressor",
        "machine_type": "L",
        "air_temperature": 302.8,
        "process_temperature": 314.1,
        "rotational_speed": 1300,
        "torque": 53,
        "tool_wear": 190,
        "status": "Critical"
    },
    {
        "machine_id": "MCH-005",
        "name": "Conveyor System",
        "machine_type": "M",
        "air_temperature": 297.8,
        "process_temperature": 307.9,
        "rotational_speed": 1520,
        "torque": 38,
        "tool_wear": 35,
        "status": "Healthy"
    },
    {
        "machine_id": "MCH-006",
        "name": "Hydraulic Press",
        "machine_type": "H",
        "air_temperature": 300.4,
        "process_temperature": 311.8,
        "rotational_speed": 1400,
        "torque": 46,
        "tool_wear": 125,
        "status": "At Risk"
    }
]


# Create a lookup dictionary for machine profile details
MACHINE_PROFILE_LOOKUP = {
    machine["machine_id"]: machine
    for machine in MACHINE_PROFILES
}


# --------------------------------------------------
# FRONTEND ROUTES
# --------------------------------------------------

@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# --------------------------------------------------
# GET ALL MACHINES
# --------------------------------------------------

@app.get("/api/machines")
def api_get_machines():

    registered_machines = db_get_machines()

    machines = []

    for machine in registered_machines:

        machine_id = machine["machine_id"]

        profile = MACHINE_PROFILE_LOOKUP.get(machine_id, {})

        combined_machine = {
            **profile,
            **machine
        }

        machines.append(combined_machine)

    return jsonify({
        "machines": machines
    }), 200


# --------------------------------------------------
# GET INDIVIDUAL MACHINE DETAILS
# --------------------------------------------------

@app.get("/api/machines/<machine_id>")
def api_get_machine(machine_id):

    machine = get_machine(machine_id)

    if machine is None:
        return jsonify({
            "error": "Machine not found."
        }), 404

    profile = MACHINE_PROFILE_LOOKUP.get(machine_id, {})

    combined_machine = {
        **profile,
        **machine
    }

    return jsonify(combined_machine), 200


# --------------------------------------------------
# GET PREDICTION HISTORY
# --------------------------------------------------

@app.get("/api/predictions")
def api_get_predictions():

    predictions = db_get_predictions()

    return jsonify({
        "predictions": predictions
    }), 200


# --------------------------------------------------
# GET FAILURE ALERTS
# --------------------------------------------------

@app.get("/api/alerts")
def api_get_alerts():

    alerts = db_get_alerts()

    return jsonify({
        "alerts": alerts
    }), 200


# --------------------------------------------------
# RESOLVE A FAILURE ALERT
# --------------------------------------------------

@app.patch("/api/alerts/<int:alert_id>/resolve")
def api_resolve_alert(alert_id):

    resolved = resolve_alert(alert_id)

    if not resolved:
        return jsonify({
            "error": "Alert not found."
        }), 404

    return jsonify({
        "message": "Alert resolved successfully.",
        "alert_id": alert_id
    }), 200



# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    return jsonify({
        "status": "ok",
        "message": "Predictive Maintenance API is running."
    }), 200


# --------------------------------------------------
# MACHINE FAILURE PREDICTION
# --------------------------------------------------

@app.post("/predict")
def predict():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send sensor readings as a JSON object."
        }), 400

    try:

        # Accept snake_case and camelCase field names
        machine_id = data.get("machine_id", data.get("machineId"))

        machine_type = data.get(
            "machine_type",
            data.get("machineType", data.get("type"))
        )

        air_temperature = data.get(
            "air_temperature",
            data.get("airTemperature")
        )

        process_temperature = data.get(
            "process_temperature",
            data.get("processTemperature")
        )

        rotational_speed = data.get(
            "rotational_speed",
            data.get("rotationalSpeed")
        )

        torque = data.get("torque")

        tool_wear = data.get(
            "tool_wear",
            data.get("toolWear")
        )

        # Validate machine registration when an ID is supplied
        if machine_id:

            registered_machine = get_machine(machine_id)

            if registered_machine is None:
                return jsonify({
                    "error": "Selected machine is not registered."
                }), 400

            if registered_machine["machine_type"] != machine_type:
                return jsonify({
                    "error": "Machine type does not match the registered machine."
                }), 400


        # Run the trained Random Forest model
        result = predict_machine_failure(
            machine_type,
            air_temperature,
            process_temperature,
            rotational_speed,
            torque,
            tool_wear
        )

        # Save prediction and generate alert in one transaction
        prediction_id, alert_id = save_prediction_with_alert(
            machine_type=machine_type,
            air_temperature=float(air_temperature),
            process_temperature=float(process_temperature),
            rotational_speed=float(rotational_speed),
            torque=float(torque),
            tool_wear=float(tool_wear),
            predicted_failure=result["predicted_failure"],
            prediction_status=result["status"],
            machine_id=machine_id,
            confidence=result.get("confidence")
        )

        return jsonify({
            "prediction_id": prediction_id,
            "machine_id": machine_id,
            "alert_id": alert_id,
            **result
        }), 200


    except (TypeError, ValueError) as error:

        return jsonify({
            "error": str(error)
        }), 400

    except Exception:

        app.logger.exception("Prediction request failed")

        return jsonify({
            "error": "Prediction failed. Check the backend terminal for details."
        }), 500


# --------------------------------------------------
# RUN FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

import math
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "random_forest_model.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found: {MODEL_PATH}\n"
        "Place random_forest_model.pkl inside the project's models/ folder."
    )

# Load the trained preprocessing + Random Forest pipeline once at startup.
model = joblib.load(MODEL_PATH)


def _to_finite_number(name, value):
    """Convert a supplied value to float and reject invalid numbers."""
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name} must be a valid number.")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a valid number.")

    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number.")

    return number


def predict_machine_failure(
    machine_type,
    air_temperature,
    process_temperature,
    rotational_speed,
    torque,
    tool_wear,
):
    """Validate sensor inputs and return the saved model's prediction."""
    if machine_type not in ("L", "M", "H"):
        raise ValueError("Machine type must be L, M, or H.")

    readings = {
        "Air temperature": _to_finite_number("Air temperature", air_temperature),
        "Process temperature": _to_finite_number("Process temperature", process_temperature),
        "Rotational speed": _to_finite_number("Rotational speed", rotational_speed),
        "Torque": _to_finite_number("Torque", torque),
        "Tool wear": _to_finite_number("Tool wear", tool_wear),
    }

    if readings["Air temperature"] <= 0:
        raise ValueError("Air temperature must be above 0 K.")
    if readings["Process temperature"] <= 0:
        raise ValueError("Process temperature must be above 0 K.")
    if readings["Rotational speed"] <= 0:
        raise ValueError("Rotational speed must be above zero.")
    if readings["Torque"] < 0:
        raise ValueError("Torque cannot be negative.")
    if readings["Tool wear"] < 0:
        raise ValueError("Tool wear cannot be negative.")

    # Keep feature names and order consistent with the model's training data.
    sample = pd.DataFrame([{
        "Type": machine_type,
        "Air temperature": readings["Air temperature"],
        "Process temperature": readings["Process temperature"],
        "Rotational speed": readings["Rotational speed"],
        "Torque": readings["Torque"],
        "Tool wear": readings["Tool wear"],
    }])

    predicted_failure = int(model.predict(sample)[0])
    status = "Failure predicted" if predicted_failure == 1 else "No failure predicted"

    return {
        "predicted_failure": predicted_failure,
        "status": status,
    }

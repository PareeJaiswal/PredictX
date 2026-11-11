
from database.db_operations import (
    initialize_database,
    save_prediction,
    get_connection
)

# 1. Initialize database
initialize_database()

print("Database initialized successfully!")


# 2. Save a sample prediction
prediction_id = save_prediction(
    machine_type="M",
    air_temperature=300.0,
    process_temperature=310.0,
    rotational_speed=1500,
    torque=40.0,
    tool_wear=100,
    predicted_failure=0,
    prediction_status="No failure predicted"
)

print("\nPrediction saved successfully!")
print("Prediction ID:", prediction_id)


# 3. Retrieve the saved record
connection = get_connection()

try:
    record = connection.execute(
        "SELECT * FROM predictions WHERE id = ?",
        (prediction_id,)
    ).fetchone()

    print("\nRetrieved database record:")
    print(dict(record))

finally:
    connection.close()

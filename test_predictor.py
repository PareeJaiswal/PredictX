
from backend.predictor import predict_machine_failure

# Test with valid sensor readings
result = predict_machine_failure(
    machine_type="M",
    air_temperature=300.0,
    process_temperature=310.0,
    rotational_speed=1500,
    torque=40.0,
    tool_wear=100
)

print("Backend prediction result:")
print(result)

from backend.predictor import predict_machine_failure

test_cases = [
    {
        "name": "High torque and tool wear",
        "machine_type": "M",
        "air_temperature": 303,
        "process_temperature": 315,
        "rotational_speed": 1200,
        "torque": 65,
        "tool_wear": 250
    },
    {
        "name": "Low speed and high torque",
        "machine_type": "M",
        "air_temperature": 305,
        "process_temperature": 317,
        "rotational_speed": 1000,
        "torque": 70,
        "tool_wear": 200
    },
    {
        "name": "High tool wear and low speed",
        "machine_type": "H",
        "air_temperature": 302,
        "process_temperature": 312,
        "rotational_speed": 1100,
        "torque": 60,
        "tool_wear": 240
    }
]

for case in test_cases:
    result = predict_machine_failure(
        machine_type=case["machine_type"],
        air_temperature=case["air_temperature"],
        process_temperature=case["process_temperature"],
        rotational_speed=case["rotational_speed"],
        torque=case["torque"],
        tool_wear=case["tool_wear"]
    )

    print(case["name"], ":", result)
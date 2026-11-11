
import joblib
import pandas as pd
from pathlib import Path

# Locate the saved model
PROJECT_ROOT = Path(__file__).resolve().parent

model_path = PROJECT_ROOT / "models" / "random_forest_model.pkl"

# Load model
model = joblib.load(model_path)

print("Model loaded successfully!")

# Create sample sensor readings
sample = pd.DataFrame([{
    "Type": "M",
    "Air temperature": 300.0,
    "Process temperature": 310.0,
    "Rotational speed": 1500,
    "Torque": 40.0,
    "Tool wear": 100
}])

# Generate prediction
prediction = model.predict(sample)

print("\nPredicted machine failure:", int(prediction[0]))

if prediction[0] == 1:
    print("Alert: Potential machine failure detected!")
else:
    print("No machine failure predicted.")

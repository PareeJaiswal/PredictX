
import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import confusion_matrix, classification_report


# 1. Find project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]


# 2. Load dataset
df = pd.read_csv(PROJECT_ROOT / "data" / "data.csv")


# 3. Standardize column names
df = df.rename(columns={
    "Air temperature [K]": "Air temperature",
    "Process temperature [K]": "Process temperature",
    "Rotational speed [rpm]": "Rotational speed",
    "Torque [Nm]": "Torque",
    "Tool wear [min]": "Tool wear"
})


# 4. Separate features and target
X = df.drop(
    columns=[
        "Machine failure",
        "TWF", "HDF", "PWF", "OSF", "RNF",
        "UDI", "Product ID"
    ],
    errors="ignore"
)

y = df["Machine failure"]


# 5. Identify feature types
categorical_features = ["Type"]

numerical_features = [
    "Air temperature",
    "Process temperature",
    "Rotational speed",
    "Torque",
    "Tool wear"
]


# 6. Prepare preprocessing
preprocessor = ColumnTransformer([
    ("num", "passthrough", numerical_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
])


# 7. Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# 8. Create Random Forest pipeline
model = Pipeline([
    ("preprocessing", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    ))
])


# 9. Train model
print("Training Random Forest model...")

model.fit(X_train, y_train)


# 10. Make predictions
y_pred = model.predict(X_test)


# 11. Evaluate model
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0
))


# 12. Save trained model
model_dir = PROJECT_ROOT / "models"
model_dir.mkdir(exist_ok=True)

model_path = model_dir / "random_forest_model.pkl"

joblib.dump(model, model_path)

print("\nRandom Forest model saved successfully!")
print("Model location:", model_path)


from ucimlrepo import fetch_ucirepo
import pandas as pd
from pathlib import Path

# Create data folder
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(exist_ok=True)

# Download UCI AI4I 2020 dataset
dataset = fetch_ucirepo(id=601)

# Combine input features and target
X = dataset.data.features
y = dataset.data.targets

df = pd.concat([X, y], axis=1)

# Save dataset
output_path = data_dir / "data.csv"
df.to_csv(output_path, index=False)

print("Dataset downloaded successfully!")
print("Dataset shape:", df.shape)
print("Saved to:", output_path)
print("\nFirst five rows:")
print(df.head())

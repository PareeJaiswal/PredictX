
import pandas as pd
from pathlib import Path

# Load dataset
data_path = Path(__file__).resolve().parent / "data" / "data.csv"
df = pd.read_csv(data_path)

print("Dataset shape:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nMachine failure distribution:")
print(df["Machine failure"].value_counts())

print("\nMachine type distribution:")
print(df["Type"].value_counts())

print("\nDataset validation completed!")

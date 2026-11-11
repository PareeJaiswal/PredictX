
from database.db_operations import (
    initialize_database,
    get_machines,
    get_predictions,
    get_alerts
)

print("Initializing database...")

initialize_database()

print("\nREGISTERED MACHINES:")
for machine in get_machines():
    print(machine)

print("\nEXISTING PREDICTIONS:")
for prediction in get_predictions():
    print(prediction)

print("\nEXISTING ALERTS:")
for alert in get_alerts():
    print(alert)

print("\nDatabase upgrade test completed!")

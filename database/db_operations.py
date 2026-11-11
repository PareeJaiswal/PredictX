
import sqlite3
from database.db_config import DATABASE_PATH


# Six demo machines used by the project
MACHINES = [
    ("MCH-001", "L"),
    ("MCH-002", "M"),
    ("MCH-003", "H"),
    ("MCH-004", "L"),
    ("MCH-005", "M"),
    ("MCH-006", "H"),
]


def get_connection():
    """Open a connection to the project's SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """
    Create the required tables and safely upgrade the existing
    predictions table without deleting existing records.
    """
    connection = get_connection()

    try:
        # Create machines table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                machine_id TEXT PRIMARY KEY,
                machine_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create predictions table if it does not exist
        connection.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_type TEXT NOT NULL,
                air_temperature REAL NOT NULL,
                process_temperature REAL NOT NULL,
                rotational_speed REAL NOT NULL,
                torque REAL NOT NULL,
                tool_wear REAL NOT NULL,
                predicted_failure INTEGER NOT NULL,
                prediction_status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check existing prediction columns
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(predictions)"
            ).fetchall()
        }

        # Add machine_id to the existing table if necessary
        if "machine_id" not in columns:
            connection.execute("""
                ALTER TABLE predictions
                ADD COLUMN machine_id TEXT
            """)

        # Add confidence if necessary
        if "confidence" not in columns:
            connection.execute("""
                ALTER TABLE predictions
                ADD COLUMN confidence REAL
            """)

        # Create alerts table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                prediction_id INTEGER,
                message TEXT NOT NULL,
                is_resolved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert demo machines without duplicating existing records
        connection.executemany("""
            INSERT OR IGNORE INTO machines (
                machine_id,
                machine_type
            )
            VALUES (?, ?)
        """, MACHINES)

        # Add indexes for faster queries
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_machine_id
            ON predictions(machine_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_created_at
            ON predictions(created_at)
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_machines():
    """Return all registered machines."""
    connection = get_connection()

    try:
        records = connection.execute("""
            SELECT machine_id, machine_type, created_at
            FROM machines
            ORDER BY machine_id
        """).fetchall()

        return [dict(record) for record in records]

    finally:
        connection.close()


def get_machine(machine_id):
    """Return one machine and its latest prediction."""
    connection = get_connection()

    try:
        machine = connection.execute("""
            SELECT machine_id, machine_type, created_at
            FROM machines
            WHERE machine_id = ?
        """, (machine_id,)).fetchone()

        if machine is None:
            return None

        latest_prediction = connection.execute("""
            SELECT *
            FROM predictions
            WHERE machine_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """, (machine_id,)).fetchone()

        result = dict(machine)
        result["latest_prediction"] = (
            dict(latest_prediction)
            if latest_prediction else None
        )

        return result

    finally:
        connection.close()


def save_prediction(
    machine_type,
    air_temperature,
    process_temperature,
    rotational_speed,
    torque,
    tool_wear,
    predicted_failure,
    prediction_status,
    machine_id=None,
    confidence=None
):
    """Save a prediction and return its database record ID."""
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO predictions (
                machine_id,
                machine_type,
                air_temperature,
                process_temperature,
                rotational_speed,
                torque,
                tool_wear,
                predicted_failure,
                prediction_status,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            machine_id,
            machine_type,
            air_temperature,
            process_temperature,
            rotational_speed,
            torque,
            tool_wear,
            predicted_failure,
            prediction_status,
            confidence
        ))

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_predictions(limit=None):
    """Return predictions with their machine IDs."""

    connection = get_connection()

    try:
        query = """
            SELECT
                p.*,
                m.machine_id AS selected_machine
            FROM predictions p
            LEFT JOIN machines m
                ON p.machine_id = m.machine_id
            ORDER BY p.created_at DESC, p.id DESC
        """

        if limit is not None:
            query += " LIMIT ?"
            records = connection.execute(query, (limit,)).fetchall()
        else:
            records = connection.execute(query).fetchall()

        return [dict(record) for record in records]

    finally:
        connection.close()


def save_alert(machine_id, prediction_id, message):
    """Save a failure alert for a registered machine."""
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO alerts (
                machine_id,
                prediction_id,
                message
            )
            VALUES (?, ?, ?)
        """, (machine_id, prediction_id, message))

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_prediction_with_alert(
    machine_type,
    air_temperature,
    process_temperature,
    rotational_speed,
    torque,
    tool_wear,
    predicted_failure,
    prediction_status,
    machine_id=None,
    confidence=None
):
    """Save prediction and alert in one transaction."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO predictions (
                machine_id,
                machine_type,
                air_temperature,
                process_temperature,
                rotational_speed,
                torque,
                tool_wear,
                predicted_failure,
                prediction_status,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            machine_id,
            machine_type,
            air_temperature,
            process_temperature,
            rotational_speed,
            torque,
            tool_wear,
            predicted_failure,
            prediction_status,
            confidence
        ))

        prediction_id = cursor.lastrowid
        alert_id = None

        if predicted_failure == 1 and machine_id:
            alert_message = (
                f"Potential failure detected for machine {machine_id}."
            )

            cursor = connection.execute("""
                INSERT INTO alerts (
                    machine_id,
                    prediction_id,
                    message
                )
                VALUES (?, ?, ?)
            """, (machine_id, prediction_id, alert_message))

            alert_id = cursor.lastrowid

        connection.commit()
        return prediction_id, alert_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_alerts(limit=None):
    """Return alerts, newest first."""

    connection = get_connection()

    try:
        query = """
            SELECT *
            FROM alerts
            ORDER BY created_at DESC, id DESC
        """

        if limit is not None:
            query += " LIMIT ?"
            records = connection.execute(query, (limit,)).fetchall()
        else:
            records = connection.execute(query).fetchall()

        return [dict(record) for record in records]

    finally:
        connection.close()

def resolve_alert(alert_id):
    """Mark an alert as resolved."""
    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE alerts
            SET is_resolved = 1
            WHERE id = ?
        """, (alert_id,))

        connection.commit()

        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(calibration_session)"))
            columns = [row[1] for row in result]
            
            if 'interval_seconds' not in columns:
                print("Adding interval_seconds column...")
                conn.execute(text("ALTER TABLE calibration_session ADD COLUMN interval_seconds INTEGER DEFAULT 60"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column already exists.")
    except Exception as e:
        print(f"Error: {e}")

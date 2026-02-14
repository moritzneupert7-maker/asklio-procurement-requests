"""
Migration script to add 'product' column to order_lines table.
Run this once to update existing databases.
"""
import sqlite3
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent.parent / "local.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}. Skipping migration.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(order_lines)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "product" in columns:
        print("Column 'product' already exists in order_lines table. Skipping migration.")
    else:
        print("Adding 'product' column to order_lines table...")
        cursor.execute("ALTER TABLE order_lines ADD COLUMN product VARCHAR(250)")
        conn.commit()
        print("Migration completed successfully.")
    
    conn.close()

if __name__ == "__main__":
    migrate()

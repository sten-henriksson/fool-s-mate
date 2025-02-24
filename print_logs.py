import sqlite3
from datetime import datetime

def print_last_10_code_logs():
    """Print the last 10 code log entries from the database"""
    try:
        # Connect to the database
        conn = sqlite3.connect('agent_logs.db')
        cursor = conn.cursor()
        
        # Query the last 10 entries
        cursor.execute("""
            SELECT timestamp, title, content 
            FROM code_logs 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        # Fetch and print the results
        logs = cursor.fetchall()
        print("\nLast 10 code logs:")
        print("=" * 80)
        for log in logs:
            timestamp, title, content = log
            # Format timestamp for better readability
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{formatted_time}] {title}:")
            print("-" * 80)
            print(content)
            print("=" * 80)
            print()
        
        # Close the connection
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    print_last_10_code_logs()

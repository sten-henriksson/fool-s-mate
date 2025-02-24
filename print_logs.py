import sqlite3

def print_last_10_logs():
    """Print the last 10 log entries from the database"""
    try:
        # Connect to the database
        conn = sqlite3.connect('agent_logs.db')
        cursor = conn.cursor()
        
        # Query the last 10 entries
        cursor.execute("""
            SELECT timestamp, level, content 
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        # Fetch and print the results
        logs = cursor.fetchall()
        print("\nLast 10 log entries:")
        print("=" * 50)
        for log in logs:
            timestamp, level, content = log
            print(f"[{timestamp}] {level}:")
            print(content)
            print("-" * 50)
        
        # Close the connection
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    print_last_10_logs()

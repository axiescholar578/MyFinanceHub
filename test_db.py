from database import get_connection

try:
    conn = get_connection()
    print("✅ Connected to Supabase successfully!")

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM expenses")

    count = cursor.fetchone()[0]

    print(f"Total records in expenses table: {count}")

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Error:")
    print(e)
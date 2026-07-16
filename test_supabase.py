from supabase_config import supabase

try:
    response = supabase.table("income").select("*").execute()

    print("✅ Connected Successfully!")
    print("Response object:")
    print(response)

    print("\nData:")
    print(response.data)

except Exception as e:
    print("❌ Error")
    print(e)
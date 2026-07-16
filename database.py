from flask import Flask, render_template
from supabase_config import supabase

app = Flask(__name__)

@app.route("/")
def home():
    response = supabase.table("income").select("*").execute()

    return render_template(
        "dashboard.html",
        incomes=response.data
    )

if __name__ == "__main__":
    app.run(debug=True)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask import Flask, render_template, request, redirect, url_for, session

from supabase_config import supabase

from services.portfolio_engine import PortfolioEngine

app = Flask(__name__)

from auth import login_manager

login_manager.init_app(app)

import os

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "myfinancehub_2026_secret_key"   # fallback for local development
)

from routes.dashboard import dashboard_bp

from routes.portfolio_dashboard import portfolio_dashboard_bp

app.register_blueprint(dashboard_bp)
# from routes.dashboard import dashboard_bp
# app.register_blueprint(dashboard_bp)
app.register_blueprint(portfolio_dashboard_bp)

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            supabase.auth.sign_up({

                "email": email,
                "password": password

            })

            return redirect(url_for("login"))

        except Exception as e:

            return str(e)

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            response = supabase.auth.sign_in_with_password({

                "email": email,
                "password": password

            })

            session["access_token"] = response.session.access_token

            session["user_id"] = response.user.id

            session["email"] = response.user.email

            return redirect(url_for("dashboard.home"))

        except Exception as e:

            return str(e)

    return render_template("login.html")
    # =====================================================
# ADD INCOME
# =====================================================

@app.route("/add-income", methods=["GET", "POST"])
def add_income():

    if request.method == "POST":

        supabase.table("income").insert({

            "income_date": request.form["income_date"],
            "source": request.form["source"],
            "category": request.form["category"],
            "amount": float(request.form["amount"]),
            "remarks": request.form["remarks"]

        }).execute()

        return redirect(url_for("dashboard.home"))

    return render_template("add_income.html")


# =====================================================
# EDIT INCOME
# =====================================================

@app.route("/edit-income/<int:id>", methods=["GET", "POST"])
def edit_income(id):

    if request.method == "POST":

        supabase.table("income").update({

            "income_date": request.form["income_date"],
            "source": request.form["source"],
            "category": request.form["category"],
            "amount": float(request.form["amount"]),
            "remarks": request.form["remarks"]

        }).eq("id", id).execute()

        return redirect(url_for("dashboard.home"))

    response = (
        supabase.table("income")
        .select("*")
        .eq("id", id)
        .single()
        .execute()
    )

    return render_template(
        "edit_income.html",
        income=response.data
    )


# =====================================================
# DELETE INCOME
# =====================================================

@app.route("/delete-income/<int:id>")
def delete_income(id):

    supabase.table("income") \
        .delete() \
        .eq("id", id) \
        .execute()

    return redirect(url_for("dashboard.home"))


# =====================================================
# ADD EXPENSE
# =====================================================

@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():

    if request.method == "POST":

        supabase.table("expenses").insert({

            "transaction_date": request.form["transaction_date"],
            "category": request.form["category"],
            "description": request.form["description"],
            "amount": float(request.form["amount"])

        }).execute()

        return redirect(url_for("dashboard.home"))

    return render_template("add_expense.html")


# =====================================================
# EDIT EXPENSE
# =====================================================

@app.route("/edit-expense/<int:id>", methods=["GET", "POST"])
def edit_expense(id):

    if request.method == "POST":

        supabase.table("expenses").update({

            "transaction_date": request.form["transaction_date"],
            "category": request.form["category"],
            "description": request.form["description"],
            "amount": float(request.form["amount"])

        }).eq("id", id).execute()

        return redirect(url_for("dashboard.home"))

    response = (
        supabase.table("expenses")
        .select("*")
        .eq("id", id)
        .single()
        .execute()
    )

    return render_template(
        "edit_expense.html",
        expense=response.data
    )


# =====================================================
# DELETE EXPENSE
# =====================================================

@app.route("/delete-expense/<int:id>")
def delete_expense(id):

    supabase.table("expenses") \
        .delete() \
        .eq("id", id) \
        .execute()

    return redirect(url_for("dashboard.home"))

print(">>> ADD HOLDING ROUTE LOADED <<<")

# =====================================================
# HOLDINGS
# =====================================================

@app.route("/holdings")
def holdings():

    response = (
        supabase
        .table("holdings")
        .select("*")
        .eq("user_id", session["user_id"])
        .order("id")
        .execute()
    )

    holdings = []

    for row in response.data:

        holdings.append({

            "id": row["id"],

            "purchase_date": row.get("purchase_date", ""),

            "asset_name": row.get("asset_name", ""),

            "ticker": row.get("ticker", ""),

            "asset_class": row.get("asset_class", ""),

            "platform": row.get("platform", ""),

            "account_name": row.get("account_name", ""),

            "country": row.get("country", ""),

            "currency": row.get("currency", ""),

            "quantity": float(row.get("quantity") or 0),

            "average_cost": float(row.get("average_cost") or 0),

            "current_price": float(row.get("current_price") or 0),

            "total_fees": float(row.get("total_fees") or 0),

            "remarks": row.get("remarks", "")

        })

    return render_template(
        "holdings.html",
        holdings=holdings
    )

@app.route("/add-holding", methods=["GET", "POST"])
def add_holding():

    if request.method == "POST":

        purchase_date = request.form["purchase_date"]
        asset_class = request.form["asset_class"]
        platform = request.form["platform"]
        account_name = request.form["account_name"]
        ticker = request.form["ticker"]
        asset_name = request.form["asset_name"]
        currency = request.form["currency"]
        country = request.form["country"]

        quantity = float(request.form["quantity"])
        average_cost = float(request.form["average_cost"])
        total_fees = float(request.form["total_fees"])
        current_price = float(request.form["current_price"])

        remarks = request.form["remarks"]

        supabase.table("holdings").insert({
            "user_id": session["user_id"],    
            "purchase_date": purchase_date,
            "asset_class": asset_class,
            "platform": platform,
            "account_name": account_name,
            "ticker": ticker,
            "asset_name": asset_name,
            "country": country,
            "currency": currency,
            "quantity": quantity,
            "average_cost": average_cost,
            "total_fees": total_fees,
            "current_price": current_price,
            "remarks": remarks

        }).execute()

        return redirect("/")

    return render_template("add_holding.html")

@app.route("/rebuild-portfolio")
def rebuild_portfolio():

    PortfolioEngine.rebuild_holdings()

    return redirect("/holdings")

@app.route("/transactions")
def transactions():

    response = (
    supabase
    .table("transactions")
    .select("*, assets(asset_name,ticker), accounts(account_name)")
    .order("transaction_date", desc=True)
    .execute()
    )

    transactions = []

    for row in response.data:

        row["asset_name"] = row["assets"]["asset_name"]
        row["account_name"] = row["accounts"]["account_name"]

        transactions.append(row)

    return render_template(
        "transactions.html",
        transactions=transactions
    )

# =====================================================
# ADD TRANSACTION
# =====================================================

@app.route("/add-transaction", methods=["GET", "POST"])
def add_transaction():

    if request.method == "POST":

        supabase.table("transactions").insert({

            "transaction_date": request.form["transaction_date"],
            "transaction_type": request.form["transaction_type"],
            "asset_id": int(request.form["asset_id"]),
            "account_id": int(request.form["account_id"]),
            "quantity": float(request.form["quantity"]),
            "price": float(request.form["price"]),
            "fees": float(request.form["fees"]),
            "exchange_rate": float(request.form["exchange_rate"]),
            "cash_amount": float(request.form["cash_amount"]),
            "remarks": request.form["remarks"]

        }).execute()

        return redirect(url_for("transactions"))

    assets = (
        supabase
        .table("assets")
        .select("*")
        .order("asset_name")
        .execute()
        .data
    )

    accounts = (
        supabase
        .table("accounts")
        .select("*")
        .order("account_name")
        .execute()
        .data
    )

    return render_template(
        "add_transaction.html",
        assets=assets,
        accounts=accounts
    )
# =====================================================
# INVESTMENT DASHBOARD
# =====================================================

@app.route("/investment")
def investment_dashboard():

    selected_year = request.args.get("year")

    query = supabase.table("holdings").select("*")

    if selected_year:

        query = query.gte(
            "purchase_date",
            f"{selected_year}-01-01"
        ).lte(
            "purchase_date",
            f"{selected_year}-12-31"
        )

    response = query.execute()

    holdings = response.data
    
    total_cost = 0
    total_value = 0

    for h in holdings:

        cost = (
            float(h["quantity"]) *
            float(h["average_cost"])
        ) + float(h["total_fees"])

        value = (
            float(h["quantity"]) *
            float(h["current_price"])
        )

        total_cost += cost
        total_value += value

    total_gain = total_value - total_cost

    if total_cost > 0:
        total_return = (total_gain / total_cost) * 100
    else:
        total_return = 0

    return render_template(

        "investment_dashboard.html",

        holdings=holdings,

        total_cost=total_cost,

        total_value=total_value,

        total_gain=total_gain,

        total_return=total_return

    )
# =====================================================
# DELETE HOLDING
# =====================================================

@app.route("/delete-holding/<int:id>")
def delete_holding(id):

    try:

        supabase.table("holdings") \
            .delete() \
            .eq("id", id) \
            .execute()

    except Exception as e:

        print(e)

    return redirect(url_for("holdings"))
# =====================================================
# EDIT HOLDING
# =====================================================

@app.route("/edit-holding/<int:id>", methods=["GET", "POST"])
def edit_holding(id):

    if request.method == "POST":

        supabase.table("holdings").update({

            "quantity": float(request.form["quantity"]),
            "average_cost": float(request.form["average_cost"]),
            "total_fees": float(request.form["total_fees"]),
            "current_price": float(request.form["current_price"]),
            "remarks": request.form["remarks"]

        }).eq("id", id).execute()

        return redirect(url_for("holdings"))

    response = (
        supabase
        .table("holdings")
        .select("*")
        .eq("id", id)
        .single()
        .execute()
    )

    if not response.data:
        return "Holding not found", 404

    return render_template(
        "edit_holding.html",
        holding=response.data
    )# =====================================================
# ADD BUDGET
# =====================================================

@app.route("/add-budget", methods=["GET", "POST"])
def add_budget():

    if request.method == "POST":

        month = request.form["month"] + "-01"

        supabase.table("budgets").insert({

            "category": request.form["category"],
            "budget_amount": float(request.form["budget_amount"]),
            "user_id": session["user_id"],
            "month": month

        }).execute()

        return redirect(url_for("dashboard.home"))

    return render_template("add_budget.html")

@app.route("/edit-budget/<int:id>", methods=["GET", "POST"])
def edit_budget(id):

    if request.method == "POST":

        month = request.form["month"] + "-01"

        supabase.table("budgets").update({

            "category": request.form["category"],
            "budget_amount": float(request.form["budget_amount"]),
            "user_id": session["user_id"],
            "month": month

        }).eq("id", id).execute()

        return redirect(url_for("dashboard.home"))

    response = (
        supabase.table("budgets")
        .select("*")
        .eq("id", id)
        .single()
        .execute()
    )

    budget = response.data

    return render_template(
        "edit_budget.html",
        budget=budget
    )

@app.route("/delete-budget/<int:id>")
def delete_budget(id):

    supabase.table("budgets") \
        .delete() \
        .eq("id", id) \
        .eq("user_id", session["user_id"]) \
        .execute()

    return redirect(url_for("dashboard.home"))
# =====================================================
# ACCOUNTS
# =====================================================

@app.route("/accounts")
def accounts():

    response = (
        supabase.table("accounts")
        .select("*")
        .eq("user_id", session["user_id"])
        .order("platform")
        .execute()
    )

    return render_template(
        "accounts.html",
        accounts=response.data
    )


@app.route("/add-account", methods=["GET", "POST"])
def add_account():

    if request.method == "POST":

        supabase.table("accounts").insert({

            "user_id": session["user_id"],

            "platform": request.form["platform"],
            "account_name": request.form["account_name"],
            "account_type": request.form["account_type"],
            "country": request.form["country"],
            "base_currency": request.form["base_currency"],
            "remarks": request.form["remarks"]

        }).execute()

        return redirect(url_for("accounts"))

    return render_template("add_account.html")

@app.route("/edit-account/<int:id>", methods=["GET", "POST"])
def edit_account(id):

    if request.method == "POST":

        supabase.table("accounts").update({

            "platform": request.form["platform"],
            "account_name": request.form["account_name"],
            "account_type": request.form["account_type"],
            "country": request.form["country"],
            "base_currency": request.form["base_currency"],
            "remarks": request.form["remarks"]

        }) \
        .eq("id", id) \
        .eq("user_id", session["user_id"]) \
        .execute()

        return redirect(url_for("accounts"))

    response = (
        supabase.table("accounts")
        .select("*")
        .eq("id", id)
        .eq("user_id", session["user_id"])
        .single()
        .execute()
    )

    return render_template(
        "edit_account.html",
        account=response.data
    )

@app.route("/delete-account/<int:id>")
def delete_account(id):

    supabase.table("accounts") \
        .delete() \
        .eq("id", id) \
        .eq("user_id", session["user_id"]) \
        .execute()

    return redirect(url_for("accounts")) 

@app.route("/update-market-prices")
def update_market_prices():

    from services.market_price_service import MarketPriceService

    holdings = (
        supabase
        .table("holdings")
        .select("id, ticker")
        .execute()
        .data
    )

    for holding in holdings:

        ticker = holding["ticker"]

        if not ticker:
            continue

        price = MarketPriceService.get_price(ticker)

        if price is not None:

            supabase.table("holdings").update({

                "current_price": price

            }).eq("id", holding["id"]).execute()

    return redirect(url_for("holdings"))

# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)

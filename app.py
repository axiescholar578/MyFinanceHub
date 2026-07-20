from flask import Flask, render_template, request, redirect, url_for

from supabase_config import supabase

from services.portfolio_engine import PortfolioEngine

app = Flask(__name__)

# from routes.dashboard import dashboard_bp
# app.register_blueprint(dashboard_bp)

@app.route("/")
def home():

    selected_month = request.args.get("month")
    
    search = request.args.get("search", "").strip()
    
    sort = request.args.get("sort", "income_date")
    
    order = request.args.get("order", "desc")

    # -------------------------
# Income
# -------------------------

    income_query = supabase.table("income").select("*")

# Month filter
    if selected_month:

        start_date = f"{selected_month}-01"

        if selected_month.endswith("-12"):
            end_date = f"{int(selected_month[:4]) + 1}-01-01"
        else:
            year, month = map(int, selected_month.split("-"))
            end_date = f"{year}-{month + 1:02d}-01"

        income_query = (
            income_query
            .gte("income_date", start_date)
            .lt("income_date", end_date)
        )

# Search filter
    if search:

        income_query = income_query.or_(
            f"source.ilike.%{search}%,category.ilike.%{search}%,remarks.ilike.%{search}%"
        )

# Sort
    income_query = income_query.order(
        sort,
        desc=(order == "desc")
    )

# Execute LAST
    incomes = income_query.execute().data

    total_income = sum(
        income["amount"] for income in incomes
    )

    # -------------------------
    # Expenses
    # -------------------------

    expense_query = supabase.table("expenses").select("*")

    if selected_month:

        start_date = f"{selected_month}-01"

        if selected_month.endswith("-12"):
            end_date = f"{int(selected_month[:4]) + 1}-01-01"
        else:
            year, month = map(int, selected_month.split("-"))
            end_date = f"{year}-{month + 1:02d}-01"

        expense_query = (
            expense_query
            .gte("transaction_date", start_date)
            .lt("transaction_date", end_date)
        )

    if search:

        expense_query = expense_query.or_(

            f"category.ilike.%{search}%,"
            f"description.ilike.%{search}%"
        )
    
    expenses = expense_query.execute().data

    total_expense = sum(
        expense["amount"] for expense in expenses
    )

    savings = total_income - total_expense

# -------------------------
# Savings Rate
# -------------------------

    if total_income > 0:
        savings_rate = round((savings / total_income) * 100, 1)
    else:
        savings_rate = 0

    # -------------------------
    # Expense Pie Chart
    # -------------------------

    expense_categories = {}

    for expense in expenses:

        category = expense["category"]

        expense_categories[category] = (
            expense_categories.get(category, 0)
            + expense["amount"]
        )

    # -------------------------
    # Budgets
    # -------------------------

    budgets = supabase.table("budgets").select("*").execute().data

    budget_summary = []

    for budget in budgets:

        spent = sum(
            expense["amount"]
            for expense in expenses
            if expense["category"] == budget["category"]
        )

        remaining = budget["budget_amount"] - spent

        percentage = (
            round(spent / budget["budget_amount"] * 100, 1)
            if budget["budget_amount"] > 0
            else 0
        )

        budget_summary.append({
            "id": budget["id"],
            "category": budget["category"],
            "budget": budget["budget_amount"],
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage
        })

    # -------------------------
    # Highest Income Source
    # -------------------------

    income_by_source = {}

    for income in incomes:

        income_by_source[income["source"]] = (
            income_by_source.get(income["source"], 0)
            + income["amount"]
        )

    if income_by_source:

        highest_income_source = max(
            income_by_source,
            key=income_by_source.get
        )

        highest_income_amount = income_by_source[
            highest_income_source
        ]

    else:

        highest_income_source = "N/A"
        highest_income_amount = 0

    # -------------------------
    # Highest Expense Category
    # -------------------------

    expense_by_category = {}

    for expense in expenses:

        expense_by_category[expense["category"]] = (
            expense_by_category.get(
                expense["category"], 0
            )
            + expense["amount"]
        )

    if expense_by_category:

        highest_expense_category = max(
            expense_by_category,
            key=expense_by_category.get
        )

        highest_expense_amount = expense_by_category[
            highest_expense_category
        ]

    else:

        highest_expense_category = "N/A"
        highest_expense_amount = 0

    # -------------------------
    # Savings Rate
    # -------------------------

    savings_rate = (
        round(savings / total_income * 100, 1)
        if total_income > 0
        else 0
    )

# -------------------------
# Monthly Trend
# -------------------------

    from collections import defaultdict

    monthly_income = defaultdict(float)
    monthly_expense = defaultdict(float)

# Income by month
    for income in supabase.table("income").select("*").execute().data:

        month = income["income_date"][:7]

        monthly_income[month] += income["amount"]

# Expense by month
    for expense in supabase.table("expenses").select("*").execute().data:

        month = expense["transaction_date"][:7]

        monthly_expense[month] += expense["amount"]

# Merge all months
    months = sorted(
        set(monthly_income.keys()) |
    set(    monthly_expense.keys())
    )

    income_trend = [
        monthly_income.get(month, 0)
        for month in months
    ]

    expense_trend = [
        monthly_expense.get(month, 0)
        for month in months
    ]

    saving_trend = [

        monthly_income.get(month, 0)
        - monthly_expense.get(month, 0)

    for month in months

    ]

# -------------------------
# Monthly Cash Flow Summary
# -------------------------

    cashflow_summary = []

    for i, month in enumerate(months):

        cashflow_summary.append({

            "month": month,

            "income": income_trend[i],

            "expense": expense_trend[i],

            "saving": saving_trend[i]

        })

# -------------------------
# Month-over-Month Growth
# -------------------------

    income_growth = 0
    expense_growth = 0
    saving_growth = 0

    if len(cashflow_summary) >= 2:

        current = cashflow_summary[-1]
        previous = cashflow_summary[-2]

    if previous["income"] > 0:
        income_growth = round(
            (current["income"] - previous["income"])
            / previous["income"] * 100,
            1
        )

    if previous["expense"] > 0:
        expense_growth = round(
            (current["expense"] - previous["expense"])
            / previous["expense"] * 100,
            1
        )

    if previous["saving"] > 0:
        saving_growth = round(
            (current["saving"] - previous["saving"])
            / previous["saving"] * 100,
            1
        )

# -------------------------
# Budget Status
# -------------------------

    budget_status = "Excellent! You are within all budgets."

    for item in budget_summary:

        if item["percentage"] >= 100:
            budget_status = f"⚠ Budget exceeded for {item['category']}"
            break

        elif item["percentage"] >= 80:
            budget_status = f"⚠ {item['category']} budget is almost full"

    return render_template(

        "dashboard.html",

        incomes=incomes,
        expenses=expenses,
        months=months,

        income_trend=income_trend,

        expense_trend=expense_trend,

        saving_trend=saving_trend,

        cashflow_summary=cashflow_summary,

        total_income=total_income,
        total_expense=total_expense,
        savings=savings,

        savings_rate=savings_rate,

        budget_status=budget_status,
        
        income_growth=income_growth,
        expense_growth=expense_growth,
        saving_growth=saving_growth,

        selected_month=selected_month,

        expense_categories=expense_categories,

        budget_summary=budget_summary,

        highest_income_source=highest_income_source,
        highest_income_amount=highest_income_amount,

        highest_expense_category=highest_expense_category,
        highest_expense_amount=highest_expense_amount,
        
        search=search

    )

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

        return redirect(url_for("home"))

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

        return redirect(url_for("home"))

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

    return redirect(url_for("home"))


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

        return redirect(url_for("home"))

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

        return redirect(url_for("home"))

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

    return redirect(url_for("home"))

print(">>> ADD HOLDING ROUTE LOADED <<<")

# =====================================================
# HOLDINGS
# =====================================================

@app.route("/holdings")
def holdings():

    response = (
        supabase
        .table("holdings")
        .select("""
            *,
            assets(
                asset_name,
                ticker,
                country,
                currency,
                asset_class
            ),
            accounts(
                account_name,
                platform
            )
        """)
        .order("id")
        .execute()
    )

    holdings = []

    for row in response.data:

        asset = row.get("assets") or {}
        account = row.get("accounts") or {}

        holdings.append({

            "id": row["id"],

            "asset_name": asset.get("asset_name", ""),

            "ticker": asset.get("ticker", ""),

            "country": asset.get("country", ""),

            "currency": asset.get("currency", ""),

            "asset_class": asset.get("asset_class", ""),

            "platform": account.get("platform", ""),

            "account_name": account.get("account_name", ""),

            "quantity": float(row["quantity"]),

            "average_cost": float(row["average_cost"]),

            "current_price": float(row.get("current_price") or 0),

            "total_fees": float(row.get("total_fees") or 0)

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

    supabase.table("holdings") \
        .delete() \
        .eq("id", id) \
        .execute()

    return redirect(url_for("holdings"))

# =====================================================
# EDIT HOLDING
# =====================================================

@app.route("/edit-holding/<int:id>", methods=["GET", "POST"])
def edit_holding(id):

    if request.method == "POST":

        supabase.table("holdings").update({

            "purchase_date": request.form["purchase_date"],
            "asset_class": request.form["asset_class"],
            "platform": request.form["platform"],
            "account_name": request.form["account_name"],
            "ticker": request.form["ticker"],
            "asset_name": request.form["asset_name"],
            "country": request.form["country"],
            "currency": request.form["currency"],
            "quantity": float(request.form["quantity"]),
            "average_cost": float(request.form["average_cost"]),
            "total_fees": float(request.form["total_fees"]),
            "current_price": float(request.form["current_price"]),
            "remarks": request.form["remarks"]

        }).eq("id", id).execute()

        return redirect(url_for("holdings"))

    response = (
        supabase.table("holdings")
        .select("*")
        .eq("id", id)
        .single()
        .execute()
    )

    return render_template(
        "edit_holding.html",
        holding=response.data
    )
    
# =====================================================
# ADD BUDGET
# =====================================================

@app.route("/add-budget", methods=["GET", "POST"])
def add_budget():

    if request.method == "POST":

        month = request.form["month"] + "-01"

        supabase.table("budgets").insert({

            "category": request.form["category"],
            "budget_amount": float(request.form["budget_amount"]),
            "month": month

        }).execute()

        return redirect(url_for("home"))

    return render_template("add_budget.html")

@app.route("/edit-budget/<int:id>", methods=["GET", "POST"])
def edit_budget(id):

    if request.method == "POST":

        month = request.form["month"] + "-01"

        supabase.table("budgets").update({

            "category": request.form["category"],
            "budget_amount": float(request.form["budget_amount"]),
            "month": month

        }).eq("id", id).execute()

        return redirect(url_for("home"))

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
        .execute()

    return redirect(url_for("home"))
# =====================================================
# ACCOUNTS
# =====================================================

@app.route("/accounts")
def accounts():

    response = (
        supabase.table("accounts")
        .select("*")
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

        }).eq("id", id).execute()

        return redirect(url_for("accounts"))

    response = (
        supabase.table("accounts")
        .select("*")
        .eq("id", id)
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
        .execute()

    return redirect(url_for("accounts"))    
# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)

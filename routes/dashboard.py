from flask import Blueprint, render_template, request, session, redirect, url_for
from supabase_config import supabase
from services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    selected_month = request.args.get("month")
    
    search = request.args.get("search", "").strip()
    
    sort = request.args.get("sort", "income_date")
    
    order = request.args.get("order", "desc")

    # -------------------------
# Income
# -------------------------
 
    incomes, total_income = DashboardService.get_income_data(
        user_id=user_id,
        selected_month=selected_month,
        search=search,
        sort=sort,
        order=order
    )
    # -------------------------
    # Expenses
    # -------------------------

    expense_query = (
        supabase.table("expenses")
        .select("*")
        .eq("user_id", user_id)
    )

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

    budgets = (
    supabase.table("budgets")
    .select("*")
    .eq("user_id", user_id)
    .execute()
    .data
    )

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
    for income in (
    supabase.table("income")
    .select("*")
    .eq("user_id", user_id)
    .execute()
    .data
    ):

        month = income["income_date"][:7]

        monthly_income[month] += income["amount"]

# Expense by month
    for expense in (
    supabase.table("expenses")
    .select("*")
    .eq("user_id", user_id)
    .execute()
    .data
    ):

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

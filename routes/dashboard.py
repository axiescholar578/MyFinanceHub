from flask import Blueprint, render_template, request
from supabase_config import supabase

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():

    selected_month = request.args.get("month")
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "income_date")
    order = request.args.get("order", "desc")

    # -------------------------
    # Income
    # -------------------------

    income_query = supabase.table("income").select("*")

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

    if search:
        income_query = income_query.or_(
            f"source.ilike.%{search}%,category.ilike.%{search}%,remarks.ilike.%{search}%"
        )

    income_query = income_query.order(
        sort,
        desc=(order == "desc")
    )

    incomes = income_query.execute().data

    total_income = sum(
        income["amount"] for income in incomes
    )

    # -------------------------
    # Expense
    # -------------------------

    expenses = supabase.table("expenses").select("*").execute().data

    total_expense = sum(
        expense["amount"] for expense in expenses
    )

    savings = total_income - total_expense

    return render_template(
        "dashboard.html",
        incomes=incomes,
        expenses=expenses,
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        selected_month=selected_month,
        search=search,
        sort=sort,
        order=order
    )
from supabase_config import supabase


class DashboardService:

    @staticmethod
    def get_income_data(selected_month=None,
                        search="",
                        sort="income_date",
                        order="desc"):

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

        # Search
        if search:

            income_query = income_query.or_(
                f"source.ilike.%{search}%,category.ilike.%{search}%,remarks.ilike.%{search}%"
            )

        # Sort
        income_query = income_query.order(
            sort,
            desc=(order == "desc")
        )

        incomes = income_query.execute().data

        total_income = sum(
            income["amount"]
            for income in incomes
        )

        return incomes, total_income
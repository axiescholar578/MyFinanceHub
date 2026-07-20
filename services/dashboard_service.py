from supabase_config import supabase


class DashboardService:

    @staticmethod
    def get_dashboard_data(selected_month=None,
                           search="",
                           sort="income_date",
                           order="desc"):

        return {}
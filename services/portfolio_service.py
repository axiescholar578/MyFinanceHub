from supabase_config import supabase


class PortfolioService:

    @staticmethod
    def get_all_transactions(user_id):

        response = (
            supabase
            .table("transactions")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        return response.data or []


    @staticmethod
    def get_all_assets(user_id):

        response = (
            supabase
            .table("assets")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        return response.data or []


    @staticmethod
    def get_all_accounts(user_id):

        response = (
            supabase
            .table("accounts")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .execute()
        )

        return response.data or []
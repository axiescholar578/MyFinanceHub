from supabase_config import supabase


class PortfolioService:

    @staticmethod
    def get_all_transactions():

        response = (
            supabase
            .table("transactions")
            .select("*")
            .execute()
        )

        return response.data


    @staticmethod
    def get_all_assets():

        response = (
            supabase
            .table("assets")
            .select("*")
            .execute()
        )

        return response.data


    @staticmethod
    def get_all_accounts():

        response = (
            supabase
            .table("accounts")
            .select("*")
            .eq("is_active", True)
            .execute()
        )

        return response.data
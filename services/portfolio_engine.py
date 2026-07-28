from collections import defaultdict
from datetime import datetime

from supabase_config import supabase


class PortfolioEngine:

    @staticmethod
    def rebuild_holdings(user_id):

        print("========== Portfolio Engine ==========")

        # -----------------------------------
        # Read this user's transactions only
        # -----------------------------------

        response = (
            supabase
            .table("transactions")
            .select("*")
            .eq("user_id", user_id)
            .order("transaction_date")
            .execute()
        )

        transactions = response.data or []

        portfolio = defaultdict(lambda: {

            "quantity": 0,
            "total_cost": 0,
            "total_fees": 0,
            "account_id": None

        })

        for trx in transactions:

            asset_id = trx["asset_id"]

            account_id = trx["account_id"]

            qty = float(trx["quantity"] or 0)

            price = float(trx["price"] or 0)

            fees = float(trx["fees"] or 0)

            trx_type = trx["transaction_type"]

            if trx_type == "BUY":

                portfolio[asset_id]["quantity"] += qty
                portfolio[asset_id]["total_cost"] += qty * price
                portfolio[asset_id]["total_fees"] += fees
                portfolio[asset_id]["account_id"] = account_id

            elif trx_type == "SELL":

                portfolio[asset_id]["quantity"] -= qty

        # -----------------------------------
        # Delete ONLY this user's holdings
        # -----------------------------------

        (
            supabase
            .table("holdings")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )

        # -----------------------------------
        # Build holdings
        # -----------------------------------

        for asset_id, data in portfolio.items():

            if data["quantity"] <= 0:
                continue

            average_cost = (

                data["total_cost"] + data["total_fees"]

            ) / data["quantity"]

            holding = {

                "user_id": user_id,

                "asset_id": asset_id,

                "account_id": data["account_id"],

                "quantity": data["quantity"],

                "average_cost": round(average_cost, 6),

                "total_fees": round(data["total_fees"], 2),

                "current_price": 0,

                "last_calculated": datetime.now().isoformat()

            }

            supabase.table("holdings").insert(holding).execute()

        print("Portfolio rebuilt successfully.")
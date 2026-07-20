from collections import defaultdict
from datetime import datetime

from supabase_config import supabase


class PortfolioEngine:

    @staticmethod
    def rebuild_holdings():

        print("Rebuilding Holdings...")

        # Read all transactions
        transactions = (
            supabase
            .table("transactions")
            .select("*")
            .order("transaction_date")
            .execute()
            .data
        )

        portfolio = defaultdict(lambda: {
            "quantity": 0,
            "cost": 0,
            "fees": 0,
            "account_id": None
        })

        for t in transactions:

            asset_id = t["asset_id"]

            qty = float(t["quantity"] or 0)

            price = float(t["price"] or 0)

            fees = float(t["fees"] or 0)

            trx = t["transaction_type"]

            if trx == "BUY":

                portfolio[asset_id]["quantity"] += qty

                portfolio[asset_id]["cost"] += qty * price

                portfolio[asset_id]["fees"] += fees

                portfolio[asset_id]["account_id"] = t["account_id"]

            elif trx == "SELL":

                portfolio[asset_id]["quantity"] -= qty

                portfolio[asset_id]["account_id"] = t["account_id"]

        # Remove existing holdings
        supabase.table("holdings").delete().neq("id", 0).execute()

        # Insert calculated holdings
        for asset_id, data in portfolio.items():

            if data["quantity"] <= 0:
                continue

            average_cost = (
                data["cost"] + data["fees"]
            ) / data["quantity"]

            holding = {
                "asset_id": asset_id,
                "account_id": data["account_id"],
                "quantity": data["quantity"],
                "average_cost": average_cost,
                "total_fees": data["fees"],
                "last_calculated": datetime.now().isoformat()
            }

            supabase.table("holdings").insert(holding).execute()

        print("Portfolio rebuild completed.")
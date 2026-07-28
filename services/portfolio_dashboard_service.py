from flask import session
from supabase_config import supabase
from services.exchange_rate_service import get_exchange_rate

class PortfolioDashboardService:

    @staticmethod
    def get_holdings(asset_class="All"):

        user_id = session["user_id"]

        query = (
            supabase
            .table("holdings")
            .select("*")
            .eq("user_id", user_id)
        )

        if asset_class != "All":
            query = query.eq("asset_class", asset_class)

        return query.execute().data


    @staticmethod
    def get_summary(asset_class="All"):

        holdings = PortfolioDashboardService.get_holdings(asset_class)

        portfolio_value = 0
        total_cost = 0

        for holding in holdings:

            rate = get_exchange_rate(holding["currency"])

            market_value = (
                float(holding["quantity"])
                * float(holding["current_price"])
                * rate
            )

            cost = (
                (
                    float(holding["quantity"])
                    * float(holding["average_cost"])
                )
                + float(holding["total_fees"] or 0)
            ) * rate

            portfolio_value += market_value
            total_cost += cost

        gain = portfolio_value - total_cost

        return_pct = (
            gain / total_cost * 100
            if total_cost > 0
            else 0
        )

        return {

            "portfolio_value": round(portfolio_value, 2),
            "total_cost": round(total_cost, 2),
            "gain": round(gain, 2),
            "return_pct": round(return_pct, 2),
            "total_holdings": len(holdings)

        }


    @staticmethod
    def get_asset_allocation(asset_class="All"):

        holdings = PortfolioDashboardService.get_holdings(asset_class)

        result = {}
        total_value = 0

        for holding in holdings:

            rate = get_exchange_rate(holding["currency"])

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
                * rate
            )

            total_value += value

            cls = holding["asset_class"]

            result[cls] = result.get(cls, 0) + value

        allocation = []

        for cls, value in result.items():

            allocation.append({

                "asset_class": cls,
                "value": round(value, 2),
                "percentage": round(
                    value / total_value * 100,
                    1
                ) if total_value > 0 else 0

            })

        allocation.sort(
            key=lambda x: x["value"],
            reverse=True
        )

        return allocation


    @staticmethod
    def get_country_allocation(asset_class="All"):

        holdings = PortfolioDashboardService.get_holdings(asset_class)

        result = {}

        for holding in holdings:

            rate = get_exchange_rate(holding["currency"])

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
                * rate
            )

            country = holding["country"]

            result[country] = result.get(country, 0) + value

        return [

            {
                "country": country,
                "value": round(value, 2)
            }

            for country, value in result.items()

        ]


    @staticmethod
    def get_platform_allocation(asset_class="All"):

        holdings = PortfolioDashboardService.get_holdings(asset_class)

        result = {}

        for holding in holdings:

            rate = get_exchange_rate(holding["currency"])

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
                * rate
            )

            platform = holding["platform"]

            result[platform] = result.get(platform, 0) + value

        return [

            {
                "platform": platform,
                "value": round(value, 2)
            }

            for platform, value in result.items()

        ]


    @staticmethod
    def get_currency_allocation(asset_class="All"):

        holdings = PortfolioDashboardService.get_holdings(asset_class)

        result = {}

        for holding in holdings:

            rate = get_exchange_rate(holding["currency"])

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
                * rate
            )

            currency = holding["currency"]

            result[currency] = result.get(currency, 0) + value

        return [

            {
                "currency": currency,
                "value": round(value, 2)
            }

            for currency, value in result.items()

        ]


    @staticmethod
    def get_top_holdings(asset_class="All"):

        holdings = PortfolioDashboardService.get_holdings(asset_class)

        top = []

        for holding in holdings:

            rate = get_exchange_rate(holding["currency"])

            market_value = (
                float(holding["quantity"])
                * float(holding["current_price"])
                * rate
            )

            cost = (
                (
                    float(holding["quantity"])
                    * float(holding["average_cost"])
                )
                + float(holding["total_fees"] or 0)
            ) * rate

            gain = market_value - cost

            pct = (
                gain / cost * 100
                if cost > 0
                else 0
            )

            top.append({

                "asset": holding["asset_name"],
                "ticker": holding["ticker"],
                "asset_class": holding["asset_class"],
                "country": holding["country"],
                "currency": holding["currency"],
                "platform": holding["platform"],
                "account_name": holding["account_name"],
                "quantity": holding["quantity"],
                "average_cost": holding["average_cost"],
                "current_price": holding["current_price"],
                "market_value": round(market_value, 2),
                "gain": round(gain, 2),
                "return_pct": round(pct, 2)

            })

        top.sort(
            key=lambda x: x["market_value"],
            reverse=True
        )

        return top
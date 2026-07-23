from supabase_config import supabase


class PortfolioDashboardService:

    @staticmethod
    def get_holdings():

        holdings = (
            supabase
            .table("holdings")
            .select("*")
            .execute()
            .data
        )

        return holdings

    @staticmethod
    def get_summary():

        holdings = PortfolioDashboardService.get_holdings()

        portfolio_value = 0
        total_cost = 0

        for holding in holdings:

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
            )

            cost = (
                float(holding["quantity"])
                * float(holding["average_cost"])
            ) + float(holding.get("total_fees") or 0)

            portfolio_value += value
            total_cost += cost

        gain = portfolio_value - total_cost

        return_pct = (
            gain / total_cost * 100
            if total_cost > 0
            else 0
        )

        return {

            "portfolio_value": portfolio_value,

            "total_cost": total_cost,

            "gain": gain,

            "return_pct": return_pct,

            "total_holdings": len(holdings)

        }

    @staticmethod
    def get_asset_allocation():

        holdings = PortfolioDashboardService.get_holdings()

        allocation = []

        for holding in holdings:

            allocation.append({

                "asset": holding["asset_name"],

                "ticker": holding["ticker"],

                "value": (
                    float(holding["quantity"])
                    * float(holding["current_price"])
                )

            })

        return allocation

    @staticmethod
    def get_country_allocation():

        holdings = PortfolioDashboardService.get_holdings()

        result = {}

        for holding in holdings:

            country = holding["country"]

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
            )

            result[country] = result.get(country, 0) + value

        return [

            {

                "country": country,

                "value": value

            }

            for country, value in result.items()

        ]

    @staticmethod
    def get_platform_allocation():

        holdings = PortfolioDashboardService.get_holdings()

        result = {}

        for holding in holdings:

            platform = holding["platform"]

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
            )

            result[platform] = result.get(platform, 0) + value

        return [

            {

                "platform": platform,

                "value": value

            }

            for platform, value in result.items()

        ]

    @staticmethod
    def get_currency_allocation():

        holdings = PortfolioDashboardService.get_holdings()

        result = {}

        for holding in holdings:

            currency = holding["currency"]

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
            )

            result[currency] = result.get(currency, 0) + value

        return [

            {

                "currency": currency,

                "value": value

            }

            for currency, value in result.items()

        ]

    @staticmethod
    def get_top_holdings():

        holdings = PortfolioDashboardService.get_holdings()

        top = []

        for holding in holdings:

            value = (
                float(holding["quantity"])
                * float(holding["current_price"])
            )

            cost = (
                float(holding["quantity"])
                * float(holding["average_cost"])
            ) + float(holding.get("total_fees") or 0)

            gain = value - cost

            pct = (
                gain / cost * 100
                if cost > 0
                else 0
            )

            top.append({

                "asset": holding["asset_name"],

                "ticker": holding["ticker"],

                "country": holding["country"],

                "currency": holding["currency"],

                "platform": holding["platform"],

                "quantity": holding["quantity"],

                "average_cost": holding["average_cost"],

                "current_price": holding["current_price"],

                "market_value": value,

                "gain": gain,

                "return_pct": pct

            })

        top.sort(

            key=lambda x: x["market_value"],

            reverse=True

        )

        return top
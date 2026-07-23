from supabase_config import supabase


def get_exchange_rate(currency):

    if currency == "SGD":
        return 1

    response = (
        supabase
        .table("exchange_rates")
        .select("exchange_rate")
        .eq("from_currency", currency)
        .eq("to_currency", "SGD")
        .order("rate_date", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return float(response.data[0]["exchange_rate"])

    return 1


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

            rate = get_exchange_rate(holding["currency"])

            value = (
                holding["quantity"]
                * holding["current_price"]
                * rate
            )

            cost = (
                holding["quantity"]
                * holding["average_cost"]
                * rate
            ) + (
                holding["total_fees"]
                * rate
            )

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

            rate = get_exchange_rate(holding["currency"])

            allocation.append({

                "asset": holding["asset_name"],
                "ticker": holding["ticker"],
                "value": (
                    holding["quantity"]
                    * holding["current_price"]
                    * rate
                )

            })

        return allocation

    @staticmethod
    def get_country_allocation():

        holdings = PortfolioDashboardService.get_holdings()

        result = {}

        for holding in holdings:

            rate = get_exchange_rate(holding["currency"])

            value = (
                holding["quantity"]
                * holding["current_price"]
                * rate
            )

            country = holding["country"]

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

            rate = get_exchange_rate(holding["currency"])

            value = (
                holding["quantity"]
                * holding["current_price"]
                * rate
            )

            platform = holding["platform"]

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

            rate = get_exchange_rate(holding["currency"])

            value = (
                holding["quantity"]
                * holding["current_price"]
                * rate
            )

            currency = holding["currency"]

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

            rate = get_exchange_rate(holding["currency"])

            value = (
                holding["quantity"]
                * holding["current_price"]
                * rate
            )

            cost = (
                holding["quantity"]
                * holding["average_cost"]
                * rate
            ) + (
                holding["total_fees"]
                * rate
            )

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
                "account_name": holding["account_name"],
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
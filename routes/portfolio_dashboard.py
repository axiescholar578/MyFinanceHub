from flask import Blueprint, render_template

from services.portfolio_dashboard_service import PortfolioDashboardService

portfolio_dashboard_bp = Blueprint(
    "portfolio_dashboard",
    __name__
)


@portfolio_dashboard_bp.route("/portfolio-dashboard")
def portfolio_dashboard():

    summary = PortfolioDashboardService.get_summary()

    asset_allocation = (
        PortfolioDashboardService.get_asset_allocation()
    )

    country_allocation = (
        PortfolioDashboardService.get_country_allocation()
    )

    platform_allocation = (
        PortfolioDashboardService.get_platform_allocation()
    )

    currency_allocation = (
        PortfolioDashboardService.get_currency_allocation()
    )

    top_holdings = (
        PortfolioDashboardService.get_top_holdings()
    )

    return render_template(

        "portfolio_dashboard.html",

        summary=summary,

        asset_allocation=asset_allocation,

        country_allocation=country_allocation,

        platform_allocation=platform_allocation,

        currency_allocation=currency_allocation,

        top_holdings=top_holdings

    )
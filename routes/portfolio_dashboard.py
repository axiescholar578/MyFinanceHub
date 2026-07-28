from flask import Blueprint, render_template, request, session, redirect, url_for
from services.portfolio_dashboard_service import PortfolioDashboardService

portfolio_dashboard_bp = Blueprint(
    "portfolio_dashboard",
    __name__
)

@portfolio_dashboard_bp.route("/portfolio-dashboard")
def portfolio_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    asset_class = request.args.get("asset_class", "All")

    summary = PortfolioDashboardService.get_summary(user_id, asset_class)

    asset_allocation = PortfolioDashboardService.get_asset_allocation(user_id, asset_class)

    country_allocation = PortfolioDashboardService.get_country_allocation(user_id, asset_class)

    platform_allocation = PortfolioDashboardService.get_platform_allocation(user_id, asset_class)

    currency_allocation = PortfolioDashboardService.get_currency_allocation(user_id, asset_class)

    top_holdings = PortfolioDashboardService.get_top_holdings(user_id, asset_class)

    return render_template(
        "portfolio_dashboard.html",
        asset_class=asset_class,
        summary=summary,
        asset_allocation=asset_allocation,
        country_allocation=country_allocation,
        platform_allocation=platform_allocation,
        currency_allocation=currency_allocation,
        top_holdings=top_holdings
    )
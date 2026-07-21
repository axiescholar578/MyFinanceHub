from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect

from supabase_config import supabase

edit_holding_bp = Blueprint(
    "edit_holding",
    __name__
)


@edit_holding_bp.route(
    "/edit-holding/<int:holding_id>",
    methods=["GET", "POST"]
)
def edit_holding(holding_id):

    # --------------------------
    # Save Changes
    # --------------------------

    if request.method == "POST":

        supabase.table("holdings").update({

            "quantity": float(request.form["quantity"]),

            "average_cost": float(request.form["average_cost"]),

            "total_fees": float(request.form["total_fees"]),

            "current_price": float(request.form["current_price"]),

            "remarks": request.form["remarks"]

        }).eq("id", holding_id).execute()

        return redirect("/holdings")



    # --------------------------
    # Load Holding
    # --------------------------

    holding = (

        supabase

        .table("holdings")

        .select("""

            *,

            assets(

                asset_name,

                ticker,

                country,

                currency

            ),

            accounts(

                account_name

            )

        """)

        .eq("id", holding_id)

        .single()

        .execute()

        .data

    )



    holding["asset_name"] = holding["assets"]["asset_name"]

    holding["ticker"] = holding["assets"]["ticker"]

    holding["country"] = holding["assets"]["country"]

    holding["currency"] = holding["assets"]["currency"]

    holding["platform"] = holding["accounts"]["account_name"]



    return render_template(

        "edit_holding.html",

        holding=holding

    )
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
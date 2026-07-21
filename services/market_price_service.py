import yfinance as yf


class MarketPriceService:

    @staticmethod
    def get_price(ticker):

        stock = yf.Ticker(ticker)

        data = stock.history(period="1d")

        if len(data) == 0:
            return None

        return round(float(data["Close"].iloc[-1]), 2)
from services.market_price_service import MarketPriceService

print(MarketPriceService.get_price("AAPL"))
print(MarketPriceService.get_price("MSFT"))
print(MarketPriceService.get_price("TSLA"))
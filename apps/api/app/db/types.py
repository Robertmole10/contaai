from sqlalchemy import Numeric

Money = Numeric(18, 2)
ExchangeRate = Numeric(18, 6)
ForeignAmount = Numeric(18, 4)
Quantity = Numeric(18, 4)
Percentage = Numeric(8, 4)
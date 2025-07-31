"""Pydantic models for order management."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "SL"
    STOP_LOSS_MARKET = "SL-M"


class ProductType(str, Enum):
    """Product type enumeration."""
    INTRADAY = "INTRADAY"
    DELIVERY = "DELIVERY"
    CARRYFORWARD = "CARRYFORWARD"


class Exchange(str, Enum):
    """Exchange enumeration."""
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    BFO = "BFO"
    MCX = "MCX"


class TradingViewWebhook(BaseModel):
    """TradingView webhook payload model."""
    
    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(OrderSide.BUY, description="Order side")
    qty: int = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, gt=0, description="Order price")
    order_type: OrderType = Field(OrderType.MARKET, description="Order type")
    product_type: ProductType = Field(ProductType.INTRADAY, description="Product type")
    exchange: Exchange = Field(Exchange.NSE, description="Exchange")
    token: Optional[str] = Field(None, description="Symbol token")
    variety: str = Field("NORMAL", description="Order variety")
    duration: str = Field("DAY", description="Order duration")
    squareoff: Optional[float] = Field(None, description="Square off price")
    stoploss: Optional[float] = Field(None, description="Stop loss price")
    
    @validator("price")
    def validate_price_for_limit_orders(cls, v, values):
        """Validate that limit orders have a price."""
        order_type = values.get("order_type")
        if order_type == OrderType.LIMIT and v is None:
            raise ValueError("Price is required for limit orders")
        return v


class SmartAPIOrder(BaseModel):
    """SmartAPI order parameters model."""
    
    variety: str
    tradingsymbol: str
    symboltoken: Optional[str]
    transactiontype: str
    exchange: str
    ordertype: str
    producttype: str
    duration: str
    price: Optional[str]
    squareoff: Optional[str]
    stoploss: Optional[str]
    quantity: str


class OrderResponse(BaseModel):
    """Order response model."""
    
    status: str
    order_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class Position(BaseModel):
    """Position model."""
    
    symbol: str
    quantity: int
    average_price: Optional[float] = None
    last_updated: Optional[str] = None
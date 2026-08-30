from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from app.schemas.stock import (
    StockCreate,
    StockIn,
    StockOut,
    StockResponse,
)
from app.schemas.sale import (
    SaleCreate,
    SaleItemCreate,
    SaleItemResponse,
    SaleResponse,
)
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)
from app.schemas.accounting import (
    AccountingMovementResponse,
    RevenueResponse,
    StockSummaryResponse,
    ProfitResponse,
    DashboardResponse,
)
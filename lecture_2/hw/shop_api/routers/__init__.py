import lecture_2.hw.shop_api.routers.carts as carts_module
import lecture_2.hw.shop_api.routers.items as items_module
from lecture_2.hw.shop_api.routers.carts import *
from lecture_2.hw.shop_api.routers.items import *

__all__ = carts_module.__all__ + items_module.__all__

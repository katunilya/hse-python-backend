from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.cart import Cart as CartModel
from app.models.cart_item import CartItem as CartItemModel

class CartService:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_cart(self, id: int) -> CartModel:
        pass
    
    def get_carts(
        self,
        offset: int = 0,
        limit=10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_quantity: Optional[int] = None,
        max_quantity: Optional[int] = None
    ) -> List[CartModel]:
        
        pass

    def add_item(self, cart_id: int, item_id: int):
        pass


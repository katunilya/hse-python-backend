from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from models import Base, Item, Cart
from schemas import ItemCreate, CartCreate, CartItem
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI()

app = FastAPI(title="Shop API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/item", response_model=schemas.ItemOut)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return 'asdafsdf'



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import Base

engine = create_engine("sqlite:///./shop.db", connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit = False, autoflush = False, bind = engine)

def get_session():
    connection = Session()
    try:
        yield connection
    finally:
       connection.close() 

Base.metadata.create_all(bind = engine)
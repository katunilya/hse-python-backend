import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError


SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@localhost:5434/online_store"

engine = None
for _ in range(100):  # Retry 10 times
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        break
    except OperationalError:
        print("Database not ready, retrying in 2 seconds...")
        time.sleep(30)
else:
    raise Exception("Could not connect to the database after 10 retries.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
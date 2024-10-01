from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from lecture_2.hw.shop_api.config import SQLALCHEMY_DATABASE_URI

__all__ = ["Session", "Base", "init_db"]

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)

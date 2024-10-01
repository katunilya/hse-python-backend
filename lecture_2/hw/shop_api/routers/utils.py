from lecture_2.hw.shop_api.storage.db import Session

__all__ = ["get_db"]


def get_db():
    """
    Creates DB connection.
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()

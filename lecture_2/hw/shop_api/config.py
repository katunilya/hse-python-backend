import os
import sys

__all__ = ["PROJECT_NAME", "API_PREFIX", "SQLALCHEMY_DATABASE_URI"]


def get_env_var(var_name: str, default_value: str = None) -> str:
    try:
        return os.environ[var_name]
    except KeyError:
        pass
    except Exception as e:
        print(f"FATAL - {e}")
        sys.exit(1)

    if default_value is not None:
        print(f"Env variable '{var_name}' not defined! Default value: '{default_value}'.")
        return str(default_value)

    print(f"Env variable '{var_name}' - Is not defined and the default value is not set! ")
    sys.exit(1)


PROJECT_NAME = "Shop API"

API_PREFIX = ""

SQLALCHEMY_DATABASE_URI = get_env_var("SQL_CONNECTION_STRING", "postgresql://postgres:postgres@localhost:5432/shop")

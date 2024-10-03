from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt

from lecture_2.rest_example import store


cart_router = APIRouter(prefix="/cart")
item_router = APIRouter(prefix="/item")


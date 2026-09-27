from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

Currency = Literal["JPY", "PHP", "USD"]
ExpenseCategory = Literal["Shopping", "Food", "Transport", "Hotel", "Activities", "Other"]


class FlightRead(BaseModel):
    origin: str
    destination: str
    date_label: str | None = None
    depart_time: str
    arrive_time: str


class FlightGroupRead(BaseModel):
    label: str
    legs: list[FlightRead]


class HotelRead(BaseModel):
    id: UUID
    city: str
    check_in: str
    check_out: str
    nights: int


class TransportLegRead(BaseModel):
    id: UUID
    origin: str
    destination: str
    duration: str
    mode: str
    detail: str
    detail_extra: str | None = None
    flag: str | None = None


class TaskRead(BaseModel):
    id: UUID
    body: str
    checked: bool


class DayRead(BaseModel):
    id: UUID
    code: str
    date_label: str
    title: str
    subtitle: str
    transit: str | None = None
    flights: list[FlightRead]
    leg: TransportLegRead | None = None
    tasks: list[TaskRead]


class PackingItemRead(BaseModel):
    id: UUID
    body: str
    checked: bool


class PackingSectionRead(BaseModel):
    id: UUID
    title: str
    items: list[PackingItemRead]


class TipRead(BaseModel):
    id: UUID
    title: str
    body: str


class ShoppingItemRead(BaseModel):
    id: UUID
    text: str
    done: bool


class ExpenseRead(BaseModel):
    id: UUID
    description: str
    amount: float
    currency: str
    category: str


class CalloutRead(BaseModel):
    title: str
    body: str


class TripRead(BaseModel):
    slug: str
    title: str
    eyebrow: str
    date_label: str
    route: list[str]
    callout: CalloutRead | None
    hotels: list[HotelRead]
    flight_groups: list[FlightGroupRead]
    days: list[DayRead]
    legs: list[TransportLegRead]
    packing: list[PackingSectionRead]
    tips: list[TipRead]
    shopping: list[ShoppingItemRead]
    expenses: list[ExpenseRead]


class CheckedUpdate(BaseModel):
    checked: bool


class ShoppingCreate(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class ShoppingUpdate(BaseModel):
    done: bool


class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, le=Decimal("10000000"))
    currency: Currency
    category: ExpenseCategory

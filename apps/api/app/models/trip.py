import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class Trip(Base, TimestampMixin):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    eyebrow: Mapped[str] = mapped_column(String(80), nullable=False)
    date_label: Mapped[str] = mapped_column(String(80), nullable=False)
    callout_title: Mapped[str | None] = mapped_column(String(200))
    callout_body: Mapped[str | None] = mapped_column(Text)

    route_stops: Mapped[list["RouteStop"]] = relationship(back_populates="trip")
    hotels: Mapped[list["Hotel"]] = relationship(back_populates="trip")
    transport_legs: Mapped[list["TransportLeg"]] = relationship(back_populates="trip")
    itinerary_days: Mapped[list["ItineraryDay"]] = relationship(back_populates="trip")
    flights: Mapped[list["Flight"]] = relationship(back_populates="trip")
    packing_sections: Mapped[list["PackingSection"]] = relationship(back_populates="trip")
    tips: Mapped[list["Tip"]] = relationship(back_populates="trip")
    shopping_items: Mapped[list["ShoppingItem"]] = relationship(back_populates="trip")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="trip")


class RouteStop(Base):
    __tablename__ = "route_stops"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)

    trip: Mapped[Trip] = relationship(back_populates="route_stops")


class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(200), nullable=False)
    check_in: Mapped[str] = mapped_column(String(80), nullable=False)
    check_out: Mapped[str] = mapped_column(String(80), nullable=False)
    nights: Mapped[int] = mapped_column(Integer, nullable=False)

    trip: Mapped[Trip] = relationship(back_populates="hotels")


class TransportLeg(Base):
    __tablename__ = "transport_legs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    origin: Mapped[str] = mapped_column(String(120), nullable=False)
    destination: Mapped[str] = mapped_column(String(120), nullable=False)
    duration: Mapped[str] = mapped_column(String(80), nullable=False)
    mode: Mapped[str] = mapped_column(String(80), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    detail_extra: Mapped[str | None] = mapped_column(Text)
    flag: Mapped[str | None] = mapped_column(Text)

    trip: Mapped[Trip] = relationship(back_populates="transport_legs")


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    date_label: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subtitle: Mapped[str] = mapped_column(Text, nullable=False)
    transit: Mapped[str | None] = mapped_column(Text)
    transport_leg_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("transport_legs.id", ondelete="SET NULL")
    )

    trip: Mapped[Trip] = relationship(back_populates="itinerary_days")
    transport_leg: Mapped[TransportLeg | None] = relationship()
    tasks: Mapped[list["ItineraryTask"]] = relationship(back_populates="day")
    flights: Mapped[list["Flight"]] = relationship(back_populates="day")


class ItineraryTask(Base):
    __tablename__ = "itinerary_tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    day_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("itinerary_days.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    day: Mapped[ItineraryDay] = relationship(back_populates="tasks")


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    day_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("itinerary_days.id", ondelete="CASCADE")
    )
    group_label: Mapped[str | None] = mapped_column(String(40))
    group_position: Mapped[int | None] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    origin: Mapped[str] = mapped_column(String(20), nullable=False)
    destination: Mapped[str] = mapped_column(String(20), nullable=False)
    date_label: Mapped[str | None] = mapped_column(String(40))
    depart_time: Mapped[str] = mapped_column(String(20), nullable=False)
    arrive_time: Mapped[str] = mapped_column(String(20), nullable=False)

    trip: Mapped[Trip] = relationship(back_populates="flights")
    day: Mapped[ItineraryDay | None] = relationship(back_populates="flights")


class PackingSection(Base):
    __tablename__ = "packing_sections"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)

    trip: Mapped[Trip] = relationship(back_populates="packing_sections")
    items: Mapped[list["PackingItem"]] = relationship(back_populates="section")


class PackingItem(Base):
    __tablename__ = "packing_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    section_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packing_sections.id", ondelete="CASCADE")
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    section: Mapped[PackingSection] = relationship(back_populates="items")


class Tip(Base):
    __tablename__ = "tips"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    trip: Mapped[Trip] = relationship(back_populates="tips")


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    trip: Mapped[Trip] = relationship(back_populates="shopping_items")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    trip: Mapped[Trip] = relationship(back_populates="expenses")

import uuid
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Expense,
    Flight,
    ItineraryDay,
    ItineraryTask,
    PackingItem,
    PackingSection,
    ShoppingItem,
    Trip,
)
from app.schemas.trip import (
    CalloutRead,
    DayRead,
    ExpenseRead,
    FlightGroupRead,
    FlightRead,
    HotelRead,
    PackingItemRead,
    PackingSectionRead,
    ShoppingItemRead,
    TaskRead,
    TipRead,
    TransportLegRead,
    TripRead,
)


class NotFoundError(Exception):
    pass


def _leg(leg) -> TransportLegRead:
    return TransportLegRead(
        id=leg.id,
        origin=leg.origin,
        destination=leg.destination,
        duration=leg.duration,
        mode=leg.mode,
        detail=leg.detail,
        detail_extra=leg.detail_extra,
        flag=leg.flag,
    )


def _flight(flight: Flight) -> FlightRead:
    return FlightRead(
        origin=flight.origin,
        destination=flight.destination,
        date_label=flight.date_label,
        depart_time=flight.depart_time,
        arrive_time=flight.arrive_time,
    )


def to_trip_read(trip: Trip) -> TripRead:
    groups: dict[str, list[Flight]] = {}
    group_order: list[str] = []
    summary_flights = [flight for flight in trip.flights if flight.group_label]
    for flight in sorted(
        summary_flights, key=lambda item: (item.group_position or 0, item.position)
    ):
        label = flight.group_label or ""
        if label not in groups:
            groups[label] = []
            group_order.append(label)
        groups[label].append(flight)

    days = sorted(trip.itinerary_days, key=lambda day: day.position)
    return TripRead(
        slug=trip.slug,
        title=trip.title,
        eyebrow=trip.eyebrow,
        date_label=trip.date_label,
        route=[stop.label for stop in sorted(trip.route_stops, key=lambda stop: stop.position)],
        callout=(
            CalloutRead(title=trip.callout_title, body=trip.callout_body)
            if trip.callout_title and trip.callout_body
            else None
        ),
        hotels=[
            HotelRead(
                id=hotel.id,
                city=hotel.city,
                check_in=hotel.check_in,
                check_out=hotel.check_out,
                nights=hotel.nights,
            )
            for hotel in sorted(trip.hotels, key=lambda hotel: hotel.position)
        ],
        flight_groups=[
            FlightGroupRead(label=label, legs=[_flight(flight) for flight in groups[label]])
            for label in group_order
        ],
        days=[
            DayRead(
                id=day.id,
                code=day.code,
                date_label=day.date_label,
                title=day.title,
                subtitle=day.subtitle,
                transit=day.transit,
                flights=[
                    _flight(flight)
                    for flight in sorted(day.flights, key=lambda flight: flight.position)
                ],
                leg=_leg(day.transport_leg) if day.transport_leg else None,
                tasks=[
                    TaskRead(id=task.id, body=task.body, checked=task.checked)
                    for task in sorted(day.tasks, key=lambda task: task.position)
                ],
            )
            for day in days
        ],
        legs=[_leg(leg) for leg in sorted(trip.transport_legs, key=lambda leg: leg.position)],
        packing=[
            PackingSectionRead(
                id=section.id,
                title=section.title,
                items=[
                    PackingItemRead(id=item.id, body=item.body, checked=item.checked)
                    for item in sorted(section.items, key=lambda item: item.position)
                ],
            )
            for section in sorted(trip.packing_sections, key=lambda section: section.position)
        ],
        tips=[
            TipRead(id=tip.id, title=tip.title, body=tip.body)
            for tip in sorted(trip.tips, key=lambda tip: tip.position)
        ],
        shopping=[
            ShoppingItemRead(id=item.id, text=item.text, done=item.done)
            for item in sorted(trip.shopping_items, key=lambda item: item.created_at)
        ],
        expenses=[
            ExpenseRead(
                id=expense.id,
                description=expense.description,
                amount=float(expense.amount),
                currency=expense.currency,
                category=expense.category,
            )
            for expense in sorted(
                trip.expenses, key=lambda expense: expense.created_at, reverse=True
            )
        ],
    )


_LOAD = (
    selectinload(Trip.route_stops),
    selectinload(Trip.hotels),
    selectinload(Trip.transport_legs),
    selectinload(Trip.itinerary_days).selectinload(ItineraryDay.tasks),
    selectinload(Trip.itinerary_days).selectinload(ItineraryDay.flights),
    selectinload(Trip.itinerary_days).selectinload(ItineraryDay.transport_leg),
    selectinload(Trip.flights),
    selectinload(Trip.packing_sections).selectinload(PackingSection.items),
    selectinload(Trip.tips),
    selectinload(Trip.shopping_items),
    selectinload(Trip.expenses),
)


async def get_trip(session: AsyncSession, slug: str) -> TripRead:
    trip = await session.scalar(select(Trip).where(Trip.slug == slug).options(*_LOAD))
    if trip is None:
        raise NotFoundError
    return to_trip_read(trip)


async def _require_trip_id(session: AsyncSession, slug: str) -> uuid.UUID:
    trip_id = await session.scalar(select(Trip.id).where(Trip.slug == slug))
    if trip_id is None:
        raise NotFoundError
    return trip_id


async def set_task_checked(
    session: AsyncSession, slug: str, task_id: uuid.UUID, checked: bool
) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    task = await session.scalar(
        select(ItineraryTask)
        .join(ItineraryDay)
        .where(ItineraryTask.id == task_id, ItineraryDay.trip_id == trip_id)
    )
    if task is None:
        raise NotFoundError
    task.checked = checked
    await session.commit()
    return await get_trip(session, slug)


async def reset_itinerary(session: AsyncSession, slug: str) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    day_ids = select(ItineraryDay.id).where(ItineraryDay.trip_id == trip_id)
    await session.execute(
        update(ItineraryTask).where(ItineraryTask.day_id.in_(day_ids)).values(checked=False)
    )
    await session.commit()
    return await get_trip(session, slug)


async def set_packing_checked(
    session: AsyncSession, slug: str, item_id: uuid.UUID, checked: bool
) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    item = await session.scalar(
        select(PackingItem)
        .join(PackingSection)
        .where(PackingItem.id == item_id, PackingSection.trip_id == trip_id)
    )
    if item is None:
        raise NotFoundError
    item.checked = checked
    await session.commit()
    return await get_trip(session, slug)


async def reset_packing(session: AsyncSession, slug: str) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    section_ids = select(PackingSection.id).where(PackingSection.trip_id == trip_id)
    await session.execute(
        update(PackingItem).where(PackingItem.section_id.in_(section_ids)).values(checked=False)
    )
    await session.commit()
    return await get_trip(session, slug)


async def add_shopping(session: AsyncSession, slug: str, text: str) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    session.add(ShoppingItem(trip_id=trip_id, text=text.strip(), done=False))
    await session.commit()
    return await get_trip(session, slug)


async def set_shopping_done(
    session: AsyncSession, slug: str, item_id: uuid.UUID, done: bool
) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    item = await session.scalar(
        select(ShoppingItem).where(ShoppingItem.id == item_id, ShoppingItem.trip_id == trip_id)
    )
    if item is None:
        raise NotFoundError
    item.done = done
    await session.commit()
    return await get_trip(session, slug)


async def delete_shopping(session: AsyncSession, slug: str, item_id: uuid.UUID) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    item = await session.scalar(
        select(ShoppingItem).where(ShoppingItem.id == item_id, ShoppingItem.trip_id == trip_id)
    )
    if item is None:
        raise NotFoundError
    await session.delete(item)
    await session.commit()
    return await get_trip(session, slug)


async def add_expense(
    session: AsyncSession,
    slug: str,
    description: str,
    amount: Decimal,
    currency: str,
    category: str,
) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    session.add(
        Expense(
            trip_id=trip_id,
            description=description.strip(),
            amount=amount,
            currency=currency,
            category=category,
        )
    )
    await session.commit()
    return await get_trip(session, slug)


async def delete_expense(session: AsyncSession, slug: str, expense_id: uuid.UUID) -> TripRead:
    trip_id = await _require_trip_id(session, slug)
    expense = await session.scalar(
        select(Expense).where(Expense.id == expense_id, Expense.trip_id == trip_id)
    )
    if expense is None:
        raise NotFoundError
    await session.delete(expense)
    await session.commit()
    return await get_trip(session, slug)

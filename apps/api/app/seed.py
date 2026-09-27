import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy import delete, select

from app.core.db import AsyncSessionLocal
from app.models import (
    Flight,
    Hotel,
    ItineraryDay,
    ItineraryTask,
    PackingItem,
    PackingSection,
    RouteStop,
    Tip,
    TransportLeg,
    Trip,
)

DATA_PATH = Path(__file__).parent / "data" / "japan_2026.json"


async def seed(force: bool) -> None:
    payload = json.loads(DATA_PATH.read_text())
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(Trip).where(Trip.slug == payload["slug"]))
        if existing and not force:
            print(f"trip {payload['slug']} already seeded")
            return
        if existing:
            await session.execute(delete(Trip).where(Trip.id == existing.id))
            await session.commit()

        callout = payload.get("callout") or {}
        trip = Trip(
            slug=payload["slug"],
            title=payload["title"],
            eyebrow=payload["eyebrow"],
            date_label=payload["date_label"],
            callout_title=callout.get("title"),
            callout_body=callout.get("body"),
        )
        session.add(trip)
        await session.flush()

        for index, label in enumerate(payload["route"]):
            session.add(RouteStop(trip_id=trip.id, position=index, label=label))

        for index, hotel in enumerate(payload["hotels"]):
            session.add(
                Hotel(
                    trip_id=trip.id,
                    position=index,
                    city=hotel["city"],
                    check_in=hotel["check_in"],
                    check_out=hotel["check_out"],
                    nights=hotel["nights"],
                )
            )

        legs: list[TransportLeg] = []
        for index, leg in enumerate(payload["legs"]):
            row = TransportLeg(
                trip_id=trip.id,
                position=index,
                origin=leg["origin"],
                destination=leg["destination"],
                duration=leg["duration"],
                mode=leg["mode"],
                detail=leg["detail"],
                detail_extra=leg.get("detail_extra"),
                flag=leg.get("flag"),
            )
            session.add(row)
            legs.append(row)
        await session.flush()

        for index, day in enumerate(payload["days"]):
            leg_index = day.get("leg_index")
            row = ItineraryDay(
                trip_id=trip.id,
                position=index,
                code=day["code"],
                date_label=day["date_label"],
                title=day["title"],
                subtitle=day["subtitle"],
                transit=day.get("transit"),
                transport_leg_id=legs[leg_index].id if leg_index is not None else None,
            )
            session.add(row)
            await session.flush()
            for task_index, task in enumerate(day["tasks"]):
                session.add(ItineraryTask(day_id=row.id, position=task_index, body=task))
            for flight_index, flight in enumerate(day.get("flights") or []):
                session.add(
                    Flight(
                        trip_id=trip.id,
                        day_id=row.id,
                        position=flight_index,
                        origin=flight["origin"],
                        destination=flight["destination"],
                        depart_time=flight["depart"],
                        arrive_time=flight["arrive"],
                    )
                )

        for group_index, group in enumerate(payload["flight_groups"]):
            for flight_index, flight in enumerate(group["legs"]):
                session.add(
                    Flight(
                        trip_id=trip.id,
                        group_label=group["label"],
                        group_position=group_index,
                        position=flight_index,
                        origin=flight["origin"],
                        destination=flight["destination"],
                        date_label=flight["date"],
                        depart_time=flight["depart"],
                        arrive_time=flight["arrive"],
                    )
                )

        for index, section in enumerate(payload["packing"]):
            row = PackingSection(trip_id=trip.id, position=index, title=section["title"])
            session.add(row)
            await session.flush()
            for item_index, item in enumerate(section["items"]):
                session.add(PackingItem(section_id=row.id, position=item_index, body=item))

        for index, tip in enumerate(payload["tips"]):
            session.add(Tip(trip_id=trip.id, position=index, title=tip["title"], body=tip["body"]))

        await session.commit()
        print(f"seeded {payload['slug']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    asyncio.run(seed(args.force))


if __name__ == "__main__":
    main()

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.trip import CheckedUpdate, ExpenseCreate, ShoppingCreate, ShoppingUpdate, TripRead
from app.services import trip_service
from app.services.trip_service import NotFoundError

router = APIRouter(prefix="/trips", tags=["trips"])


def _missing() -> HTTPException:
    return HTTPException(status_code=404, detail="Not found")


@router.get("/{slug}", response_model=TripRead)
async def read_trip(slug: str, db: AsyncSession = Depends(get_db)) -> TripRead:
    try:
        return await trip_service.get_trip(db, slug)
    except NotFoundError:
        raise _missing() from None


@router.patch("/{slug}/tasks/{task_id}", response_model=TripRead)
async def update_task(
    slug: str, task_id: UUID, body: CheckedUpdate, db: AsyncSession = Depends(get_db)
) -> TripRead:
    try:
        return await trip_service.set_task_checked(db, slug, task_id, body.checked)
    except NotFoundError:
        raise _missing() from None


@router.post("/{slug}/itinerary/reset", response_model=TripRead)
async def reset_itinerary(slug: str, db: AsyncSession = Depends(get_db)) -> TripRead:
    try:
        return await trip_service.reset_itinerary(db, slug)
    except NotFoundError:
        raise _missing() from None


@router.patch("/{slug}/packing/{item_id}", response_model=TripRead)
async def update_packing_item(
    slug: str, item_id: UUID, body: CheckedUpdate, db: AsyncSession = Depends(get_db)
) -> TripRead:
    try:
        return await trip_service.set_packing_checked(db, slug, item_id, body.checked)
    except NotFoundError:
        raise _missing() from None


@router.post("/{slug}/packing/reset", response_model=TripRead)
async def reset_packing(slug: str, db: AsyncSession = Depends(get_db)) -> TripRead:
    try:
        return await trip_service.reset_packing(db, slug)
    except NotFoundError:
        raise _missing() from None


@router.post("/{slug}/shopping", response_model=TripRead)
async def create_shopping_item(
    slug: str, body: ShoppingCreate, db: AsyncSession = Depends(get_db)
) -> TripRead:
    try:
        return await trip_service.add_shopping(db, slug, body.text)
    except NotFoundError:
        raise _missing() from None


@router.patch("/{slug}/shopping/{item_id}", response_model=TripRead)
async def update_shopping_item(
    slug: str, item_id: UUID, body: ShoppingUpdate, db: AsyncSession = Depends(get_db)
) -> TripRead:
    try:
        return await trip_service.set_shopping_done(db, slug, item_id, body.done)
    except NotFoundError:
        raise _missing() from None


@router.delete("/{slug}/shopping/{item_id}", response_model=TripRead)
async def remove_shopping_item(
    slug: str, item_id: UUID, db: AsyncSession = Depends(get_db)
) -> TripRead:
    try:
        return await trip_service.delete_shopping(db, slug, item_id)
    except NotFoundError:
        raise _missing() from None


@router.post("/{slug}/expenses", response_model=TripRead)
async def create_expense(
    slug: str, body: ExpenseCreate, db: AsyncSession = Depends(get_db)
) -> TripRead:
    try:
        return await trip_service.add_expense(
            db, slug, body.description, body.amount, body.currency, body.category
        )
    except NotFoundError:
        raise _missing() from None


@router.delete("/{slug}/expenses/{expense_id}", response_model=TripRead)
async def remove_expense(
    slug: str, expense_id: UUID, db: AsyncSession = Depends(get_db)
) -> TripRead:
    try:
        return await trip_service.delete_expense(db, slug, expense_id)
    except NotFoundError:
        raise _missing() from None

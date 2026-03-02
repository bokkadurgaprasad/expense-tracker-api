"""
API routes for CreditCard management
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from app.models.credit_card import CreditCard, CreditCardCreate, CreditCardUpdate
from app.services.credit_card_service import CreditCardService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/credit-cards", tags=["Credit Cards"])


@router.post("", response_model=CreditCard, status_code=201)
def create_credit_card(
    data: CreditCardCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new credit card"""
    service = CreditCardService()
    return service.create_card(user_id, data)


@router.get("", response_model=Dict[str, Any])
def get_credit_cards(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user_id)
):
    """Get all credit cards for the authenticated user with pagination"""
    service = CreditCardService()
    skip = (page - 1) * page_size
    return service.get_cards(user_id, skip, page_size)


@router.get("/{card_id}", response_model=CreditCard)
def get_credit_card(
    card_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific credit card"""
    service = CreditCardService()
    return service.get_card(user_id, card_id)


@router.put("/{card_id}", response_model=CreditCard)
def update_credit_card(
    card_id: str,
    data: CreditCardUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update a credit card"""
    service = CreditCardService()
    return service.update_card(user_id, card_id, data)


@router.delete("/{card_id}", status_code=204)
def delete_credit_card(
    card_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a credit card"""
    service = CreditCardService()
    service.delete_card(user_id, card_id)
    return None

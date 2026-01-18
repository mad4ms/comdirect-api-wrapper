from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Account:
    id: str
    currency: str
    balance: Decimal
    available: Optional[Decimal]


@dataclass(frozen=True)
class Transaction:
    account_id: str
    booking_date: date
    amount: Decimal
    currency: str
    purpose: Optional[str]
    type: str


@dataclass(frozen=True)
class Depot:
    id: str  # depotId
    display_id: str  # depotDisplayId
    client_id: Optional[str]


@dataclass(frozen=True)
class DepotPosition:
    depot_id: str
    position_id: str
    wkn: Optional[str]
    quantity: Decimal
    quantity_unit: str
    current_value: Decimal
    current_value_currency: str
    purchase_value: Decimal
    purchase_value_currency: str
    profit_loss_purchase_abs: Optional[Decimal]
    profit_loss_purchase_rel: Optional[str]  # Keeping as string for now as it's pre-formatted often
    profit_loss_prev_day_abs: Optional[Decimal]
    profit_loss_prev_day_rel: Optional[str]
    instrument_name: Optional[str]


@dataclass(frozen=True)
class DepotBalance:
    depot_id: str
    date_last_update: Optional[str]
    current_value: Decimal
    current_value_currency: str
    purchase_value: Decimal
    purchase_value_currency: str
    prev_day_value: Decimal
    prev_day_value_currency: str
    profit_loss_purchase_abs: Optional[Decimal]
    profit_loss_purchase_rel: Optional[str]
    profit_loss_prev_day_abs: Optional[Decimal]
    profit_loss_prev_day_rel: Optional[str]


@dataclass(frozen=True)
class Document:
    id: str
    name: str
    date_creation: str
    mime_type: str
    advertisement: bool

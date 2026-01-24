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
class AccountHolder:
    holder_name: Optional[str]
    iban: Optional[str]
    bic: Optional[str]


@dataclass(frozen=True)
class Transaction:
    account_id: str
    booking_date: date
    amount: Decimal
    currency: str
    purpose: Optional[str]
    type: str  # This is transaction_type.key from API

    # Extended fields
    reference: Optional[str] = None
    booking_status: Optional[str] = None
    valuta_date: Optional[date] = None

    # DirectDebit specific
    direct_debit_creditor_id: Optional[str] = None
    direct_debit_mandate_id: Optional[str] = None
    end_to_end_reference: Optional[str] = None

    new_transaction: bool = False

    # Counterparties
    remitter: Optional[AccountHolder] = None
    debtor: Optional[AccountHolder] = None
    creditor: Optional[AccountHolder] = None


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

from dataclasses import dataclass
from enum import Enum
from .common import Amount, IsoDate


class TransactionType(Enum):
    DIRECT_DEBIT = "DIRECT_DEBIT"
    TRANSFER = "TRANSFER"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_api(cls, key):
        return cls.__members__.get(key, cls.UNKNOWN)


@dataclass(frozen=True)
class AccountBalance:
    account_id: str
    balance: Amount
    balance_eur: Amount

    @classmethod
    def from_api(cls, data):
        return cls(
            account_id=data["accountId"],
            balance=Amount.from_api(data["balance"]),
            balance_eur=Amount.from_api(data["balanceEUR"]),
        )


@dataclass(frozen=True)
class AccountTransaction:
    amount: Amount
    booking_date: IsoDate | None
    transaction_type: TransactionType

    @classmethod
    def from_api(cls, data):
        return cls(
            amount=Amount.from_api(data["amount"]),
            booking_date=(IsoDate.from_string(data["bookingDate"]) if data.get("bookingDate") else None),
            transaction_type=TransactionType.from_api(data["transactionType"]["key"]),
        )

from dataclasses import dataclass
from decimal import Decimal
import datetime


@dataclass(frozen=True)
class Amount:
    value: Decimal
    currency: str

    @classmethod
    def from_api(cls, data):
        return cls(Decimal(data["value"]), data["unit"])


@dataclass(frozen=True)
class IsoDate:
    value: datetime.date

    @classmethod
    def from_string(cls, s: str):
        return cls(datetime.datetime.strptime(s, "%Y-%m-%d").date())

    def __str__(self):
        return self.value.isoformat()

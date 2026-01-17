from dataclasses import dataclass


@dataclass(frozen=True)
class Depot:
    depot_id: str
    holder_name: str | None

    @classmethod
    def from_api(cls, data):
        return cls(
            depot_id=data.get("depotId"),
            holder_name=data.get("holderName"),
        )


@dataclass(frozen=True)
class DepotPosition:
    wkn: str
    quantity: float
    current_value: float
    purchase_value: float
    profit_loss_purchase_abs: float
    profit_loss_purchase_rel: float
    profit_loss_prev_day_abs: float
    profit_loss_prev_day_rel: float

    @classmethod
    def from_api(cls, data):
        return cls(
            wkn=data.get("wkn"),
            quantity=data.get("quantity", {}).get("value", 0),
            current_value=data.get("currentValue", {}).get("value", 0),
            purchase_value=data.get("purchaseValue", {}).get("value", 0),
            profit_loss_purchase_abs=data.get("profitLossPurchaseAbs", {}).get("value", 0),
            profit_loss_purchase_rel=data.get("profitLossPurchaseRel", 0),
            profit_loss_prev_day_abs=data.get("profitLossPrevDayAbs", {}).get("value", 0),
            profit_loss_prev_day_rel=data.get("profitLossPrevDayRel", 0),
        )


@dataclass(frozen=True)
class DepotBalance:
    depot: Depot
    prev_day_value: float
    current_value: float
    purchase_value: float
    profit_loss_purchase_abs: float
    profit_loss_purchase_rel: float
    profit_loss_prev_day_rel: float

    @classmethod
    def from_api(cls, data):
        return cls(
            depot=Depot.from_api(data.get("depot", {})),
            prev_day_value=data.get("prevDayValue", {}).get("value", 0),
            current_value=data.get("currentValue", {}).get("value", 0),
            purchase_value=data.get("purchaseValue", {}).get("value", 0),
            profit_loss_purchase_abs=data.get("profitLossPurchaseAbs", {}).get("value", 0),
            profit_loss_purchase_rel=data.get("profitLossPurchaseRel", 0),
            profit_loss_prev_day_rel=data.get("profitLossPrevDayRel", 0),
        )

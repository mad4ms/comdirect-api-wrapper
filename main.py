import pandas as pd
from pathlib import Path
import re

# -----------------------------
# Konfiguration
# -----------------------------
CSV_PATH = Path("data/umsaetze_1188570657_20260117-0903.csv")

CATEGORY_RULES = {
    "Steuern": r"Steuer|Vorabpauschale|InvStG",
    "Energie": r"Q1 Energie",
    "Amazon": r"AMZN|AMAZON",
    "PayPal": r"PayPal",
    "Haushalt": r"DM Drogerie|Drogerie",
    "Überweisung privat": r"Mona Kuhnhenn",
    "Miete": r"Miete Nebenkosten",
    "Handwerker": r"Haustechnik|RE\d+",
    "Versicherung": r"Debeka",
}

# -----------------------------
# Laden & Bereinigung
# -----------------------------
df = pd.read_csv(
    CSV_PATH,
    sep=";",
    encoding="utf-8",
    decimal=",",
    parse_dates=["Buchungstag", "Wertstellung (Valuta)"],
    dayfirst=True,
)

# Spaltennamen vereinheitlichen
df.columns = [c.strip() for c in df.columns]

# Betrag normalisieren
df["Umsatz in EUR"] = (
    df["Umsatz in EUR"]
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)


# -----------------------------
# Kategorisierung
# -----------------------------
def categorize(text: str) -> str:
    for category, pattern in CATEGORY_RULES.items():
        if re.search(pattern, text, re.IGNORECASE):
            return category
    return "Sonstiges"


df["Kategorie"] = df["Buchungstext"].apply(categorize)

# -----------------------------
# Analyse
# -----------------------------
summary_by_category = (
    df.groupby("Kategorie")["Umsatz in EUR"].sum().sort_values()
)

summary_income_expense = {
    "Einnahmen": df.loc[df["Umsatz in EUR"] > 0, "Umsatz in EUR"].sum(),
    "Ausgaben": df.loc[df["Umsatz in EUR"] < 0, "Umsatz in EUR"].sum(),
}

# -----------------------------
# Ausgabe
# -----------------------------
print("\n=== Summe nach Kategorie ===")
print(summary_by_category)

print("\n=== Einnahmen vs. Ausgaben ===")
for k, v in summary_income_expense.items():
    print(f"{k}: {v:,.2f} EUR")

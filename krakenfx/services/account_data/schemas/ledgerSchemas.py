# krakenfx/api/schemas/ledger.py
from typing import Dict, List, Optional

from pydantic import BaseModel


class SchemasLedger(BaseModel):
    aclass: str  # Asset class (string, e.g., "currency")
    amount: str  # Transaction amount (string, representing a decimal)
    asset: str  # Asset (string, e.g., "XBT", "ETH")
    balance: str  # Account balance after transaction (string, representing a decimal)
    fee: str  # Transaction fee (string, representing a decimal)
    refid: str  # Reference ID (string)
    time: float  # Unix timestamp (integer or float)
    type: str  # Type of ledger entry (string, e.g., [none, trade, deposit, withdrawal, transfer, margin, adjustment, rollover, spend, receive, settled, credit, staking, reward, dividend, sale, conversion, nfttrade, nftcreatorfee, nftrebate, custodytransfer])
    subtype: Optional[str] = (
        None  # Additional info related to the type of ledger entry (optional, string)
    )

    model_config = {"from_attributes": True}


class SchemasLedgers(BaseModel):
    ledgers: Dict[str, SchemasLedger]


class SchemasLedgerResult(BaseModel):
    count: int
    ledger: Dict[str, SchemasLedger]


class SchemasLedgerQueryResponse(BaseModel):
    error: List[str]
    result: Dict[str, SchemasLedger]


class SchemasLedgerResponse(BaseModel):
    error: List[str]
    result: SchemasLedgerResult


""" LedgerEntry: Represents a single ledger entry with fields corresponding to the JSON structure from the Kraken API.
    refid: Reference ID of the ledger entry.
    time: Unix timestamp of the ledger entry.
    type: Type of the ledger entry (e.g., trade, deposit).
    subtype: Additional info relating to the ledger entry type, if applicable.
    aclass: Asset class (e.g., currency).
    asset: The asset involved in the ledger entry (e.g., BTC, USD).
    amount: Transaction amount.
    fee: Transaction fee.
    balance: Resulting balance after the transaction.

LedgerResult: Contains the count of ledger entries and a dictionary (ledger) where keys are ledger IDs and values are LedgerEntry instances.
    count: Total number of ledger entries.
    ledger: Dictionary mapping ledger IDs to LedgerEntry objects.

LedgerResponse: Represents the entire response from the get_ledgers API, including the result and potential errors.
    result: An instance of LedgerResult containing the ledger entries.
    error: A list of errors returned by the API, if any. """

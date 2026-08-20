"""Persistence port for the FlightTracker read API.

The API depends on this contract, not on a particular database SDK. Cassandra
will implement the same contract during the migration from Firestore.
"""

from typing import Optional, Protocol

from google.cloud import firestore


class FlightRepository(Protocol):
    def list_flights(
        self, airline: Optional[str], flight_date: Optional[str], limit: int
    ) -> list[dict]:
        """Return flights using the canonical API filter names."""


class FirestoreFlightRepository:
    """Temporary Firestore projection implementation of the read port."""

    def __init__(self) -> None:
        self._db = firestore.Client()

    def list_flights(
        self, airline: Optional[str], flight_date: Optional[str], limit: int
    ) -> list[dict]:
        query = self._db.collection("flights")

        if airline:
            query = query.where(filter=firestore.FieldFilter("carrier", "==", airline.upper()))
        if flight_date:
            query = query.where(filter=firestore.FieldFilter("flight_date", "==", flight_date))

        return [document.to_dict() for document in query.limit(limit).stream()]

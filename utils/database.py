"""Database helpers.

The original project assumed a MongoDB connection string would always be
available which meant simply importing ``utils.database`` without a
``MONGO_URL`` environment variable raised an exception.  That made running
the application locally – or executing automated tests in CI – impossible
without provisioning an external database.

To make the service easier to work with we now fall back to an in-memory
implementation when a connection string has not been provided (or when the
``motor`` dependency itself is unavailable).  The in-memory adapter supports
the subset of the Motor API that the project relies on: ``find_one`` with a
``sort`` parameter and ``insert_one`` for the ``assessments``, ``players`` and
``training_programs`` collections.  This keeps the production behaviour
unchanged while dramatically improving the developer experience.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Iterable, List, MutableMapping, Optional

try:  # pragma: no cover - exercised in integration environments
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
except ImportError:  # pragma: no cover - motor is available in prod but not required for tests
    AsyncIOMotorClient = None  # type: ignore
    AsyncIOMotorDatabase = None  # type: ignore


def _load_database() -> Optional["AsyncIOMotorDatabase"]:
    """Return a Motor database when a connection string is configured."""

    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url or AsyncIOMotorClient is None:
        return None

    db_name = os.getenv("DB_NAME", "yoyo_db")
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name]


@dataclass
class _InsertOneResult:
    inserted_id: Any


class _InMemoryCollection:
    """A tiny asynchronous stand-in for a Mongo collection."""

    def __init__(self) -> None:
        self._documents: List[MutableMapping[str, Any]] = []
        self._lock = asyncio.Lock()

    async def find_one(
        self, query: MutableMapping[str, Any], sort: Optional[Iterable] = None
    ) -> Optional[MutableMapping[str, Any]]:
        async with self._lock:
            candidates = [
                doc
                for doc in self._documents
                if all(doc.get(key) == value for key, value in query.items())
            ]

            if not candidates:
                return None

            if sort:
                key, direction = next(iter(sort))
                reverse = direction == -1
                candidates.sort(
                    key=lambda doc: doc.get(key),
                    reverse=reverse,
                )

            # Return a shallow copy to mirror Motor's behaviour where the
            # returned document is detached from the internal storage.
            return dict(candidates[0])

    async def insert_one(self, document: MutableMapping[str, Any]) -> _InsertOneResult:
        async with self._lock:
            self._documents.append(dict(document))
            inserted_id = document.get("_id", len(self._documents))
            return _InsertOneResult(inserted_id=inserted_id)


class _InMemoryDatabase:
    def __init__(self) -> None:
        self.assessments = _InMemoryCollection()
        self.players = _InMemoryCollection()
        self.training_programs = _InMemoryCollection()


# ``db`` mimics the original module level attribute so importing code does not
# have to change.  Production will receive a Motor client, while tests and
# local development fall back to the lightweight implementation.
db = _load_database() or _InMemoryDatabase()


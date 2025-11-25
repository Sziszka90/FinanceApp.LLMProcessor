from abc import ABC, abstractmethod
from typing import List
from database.entities.MatchTransaction import MatchTransaction

class IMatchTransactionRepository(ABC):
    @abstractmethod
    async def save_match_transaction(self, transaction: str, transaction_group: str) -> MatchTransaction:
        """Save a single transaction match to the database."""
        pass

    @abstractmethod
    async def save_match_transactions(self, matches: dict[str, str]) -> List[MatchTransaction]:
        """Save multiple transaction matches to the database."""
        pass

    @abstractmethod
    async def get_match_transaction(self, transaction: str) -> MatchTransaction:
        """Get a transaction match by transaction name."""
        pass

    @abstractmethod
    async def delete_match_transaction(self, transaction: str) -> bool:
        """Delete a transaction match by transaction name."""
        pass

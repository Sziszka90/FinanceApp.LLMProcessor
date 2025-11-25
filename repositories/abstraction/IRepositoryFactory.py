from abc import ABC, abstractmethod
from repositories.abstraction.IMatchTransactionRepository import IMatchTransactionRepository

class IRepositoryFactory(ABC):
    @abstractmethod
    def create_match_transaction_repository(self) -> IMatchTransactionRepository:
        """Create a new repository instance with a fresh DB session"""
        pass

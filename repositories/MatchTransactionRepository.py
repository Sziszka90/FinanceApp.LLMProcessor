from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database.entities.MatchTransaction import MatchTransaction
from repositories.abstraction.IMatchTransactionRepository import IMatchTransactionRepository
from services.abstraction.ILoggerService import ILoggerService

class MatchTransactionRepository(IMatchTransactionRepository):
    def __init__(self, db: AsyncSession, logger: ILoggerService):
        self.db = db
        self.logger = logger

    async def save_match_transaction(self, transaction: str, transaction_group: str) -> MatchTransaction:
        """Save a single transaction match to the database."""
        try:
            stmt = select(MatchTransaction).where(MatchTransaction.Transaction == transaction)
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.TransactionGroup = transaction_group
                await self.db.commit()
                await self.db.refresh(existing)
                self.logger.info(f"Updated transaction match: {transaction} -> {transaction_group}")
                return existing
            else:
                match = MatchTransaction(
                    Transaction=transaction,
                    TransactionGroup=transaction_group
                )
                self.db.add(match)
                await self.db.commit()
                await self.db.refresh(match)
                self.logger.info(f"Saved transaction match: {transaction} -> {transaction_group}")
                return match
                
        except IntegrityError as e:
            await self.db.rollback()
            self.logger.error(f"Error saving transaction match: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Unexpected error saving transaction match: {e}")
            raise

    async def save_match_transactions(self, matches: dict[str, str]) -> List[MatchTransaction]:
        """Save multiple transaction matches to the database."""
        saved_matches = []
        
        try:
            for transaction, transaction_group in matches.items():
                match = await self.save_match_transaction(transaction, transaction_group)
                saved_matches.append(match)
            
            self.logger.info(f"Saved {len(saved_matches)} transaction matches")
            return saved_matches
            
        except Exception as e:
            self.logger.error(f"Error saving multiple transaction matches: {e}")
            raise

    async def get_match_transaction(self, transaction: str) -> MatchTransaction:
        """Get a transaction match by transaction name."""
        try:
            stmt = select(MatchTransaction).where(MatchTransaction.Transaction == transaction)
            result = await self.db.execute(stmt)
            match = result.scalar_one_or_none()
            
            if match:
                self.logger.info(f"Found transaction match: {transaction}")
            else:
                self.logger.info(f"No match found for transaction: {transaction}")
            
            return match
            
        except Exception as e:
            self.logger.error(f"Error getting transaction match: {e}")
            raise

    async def delete_match_transaction(self, transaction: str) -> bool:
        """Delete a transaction match by transaction name."""
        try:
            stmt = select(MatchTransaction).where(MatchTransaction.Transaction == transaction)
            result = await self.db.execute(stmt)
            match = result.scalar_one_or_none()
            
            if match:
                await self.db.delete(match)
                await self.db.commit()
                self.logger.info(f"Deleted transaction match: {transaction}")
                return True
            else:
                self.logger.info(f"No match found to delete for transaction: {transaction}")
                return False
                
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error deleting transaction match: {e}")
            raise

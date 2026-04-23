import datetime
import json
import logging
import os
from typing import Optional

import sqlalchemy as db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.orm.session import Session

logger = logging.getLogger(__name__)


class JSONEncodedList(db.types.TypeDecorator):
    """Custom SQLAlchemy type decorator for storing a list as a JSON string."""

    impl = db.TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect) -> str:
        """Serializes list to JSON string for database storage."""
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        """Deserializes JSON string to list from database storage."""
        if value is None or value == "":
            return []
        return json.loads(value)


class Base(DeclarativeBase):
    """Base class for database models."""
    pass


class Transaction(Base):
    """Database model representing a financial transaction."""

    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String)
    amount: Mapped[float] = mapped_column(db.Float)
    category: Mapped[str] = mapped_column(db.String)
    date: Mapped[datetime.date] = mapped_column(db.Date)
    file_paths: Mapped[Optional[list[str]]] = mapped_column(
        MutableList.as_mutable(JSONEncodedList), default=[]
    )

    def __eq__(self, other: object) -> bool:
        """Compares two transactions for equality."""
        if not isinstance(other, Transaction):
            return NotImplemented
        return (
            self.name == other.name
            and self.amount == other.amount
            and self.category == other.category
            and self.date == other.date
            and set(self.file_paths or []) == set(other.file_paths or [])
        )

    def __repr__(self) -> str:
        """Returns a string representation of the Transaction object."""
        return (
            f"Transaction(id={self.id}, name={self.name}, amount={self.amount}, "
            f"category={self.category}, date={self.date}, file_paths={self.file_paths})"
        )

    def get_type(self) -> str:
        """Returns the type of the transaction ('Expense' or 'Income')."""
        return "Expense" if self.amount < 0 else "Income"

    def get_file_paths(self) -> str:
        """Returns a space-separated string of file base names."""
        separator = " "
        if self.file_paths is not None:
            return separator.join(os.path.basename(path) for path in self.file_paths)
        return ""


class DBManager:
    """Manager class for database interactions using SQLAlchemy."""

    def __init__(self, db_name: str = "cashflow"):
        """Initializes the database manager and creates the database schema."""
        self.engine = db.create_engine(f"sqlite:///{db_name}.db")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self) -> sessionmaker[Session]:
        """Returns a session maker for the database."""
        return self.Session

    def print_db(self):
        """Logs all transactions stored in the database."""
        with self.Session() as session:
            stmt = db.select(Transaction)
            transactions = session.scalars(stmt).all()

            for transaction in transactions:
                logger.info(transaction)

    def insert(self, t: Transaction) -> bool:
        """Inserts a new transaction into the database.

        Args:
            t: The Transaction object to insert.

        Returns:
            True if insertion is successful, False otherwise.
        """
        with self.Session() as session:
            session.add(t)
            try:
                session.commit()
                return True
            except IntegrityError as e:
                logger.error(f"Insert failed due to integrity error: {e}")
                return False
            except Exception as e:
                logger.error(f"Insert failed due to exception: {e}")
                return False

    def delete(self, id_to_delete: int) -> bool:
        """Deletes a transaction from the database by ID.

        Args:
            id_to_delete: The ID of the transaction to delete.

        Returns:
            True if deletion is successful, False otherwise.
        """
        with self.Session() as session:
            stmt = db.delete(Transaction).where(Transaction.id == id_to_delete)
            result = session.execute(stmt)
            if result.rowcount > 0:
                session.commit()
                logger.info(f"Transaction with id={id_to_delete} deleted.")
                return True
            else:
                logger.warning(f"No transaction found with id={id_to_delete}.")
                session.rollback()
                return False

    def update(
        self,
        id: int,
        name: str | None = None,
        amount: float | None = None,
        category: str | None = None,
        date: datetime.date | None = None,
        file_paths: list[str] | None = None,
    ) -> bool:
        """Updates an existing transaction in the database.

        Args:
            id: The ID of the transaction to update.
            name: New name, if provided.
            amount: New amount, if provided.
            category: New category, if provided.
            date: New date, if provided.
            file_paths: New file paths, if provided.

        Returns:
            True if update is successful, False otherwise.
        """
        with self.Session() as session:
            t = session.get(Transaction, id)
            if t is None:
                logger.warning(f"No transaction found with id={id}.")
                return False

            logger.info(f"{t}: Transaction to update")
            stmt = (
                db.update(Transaction)
                .where(Transaction.id == id)
                .values(
                    name=name if name is not None else t.name,
                    amount=amount if amount is not None else t.amount,
                    category=category if category is not None else t.category,
                    date=date if date is not None else t.date,
                    file_paths=file_paths,
                )
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                logger.warning(f"No transaction found with id={id} to update.")
                return False
            session.commit()
            logger.info(f"{t}: updated successfully ")
            return True

    def select_id(self, id: int) -> Transaction | None:
        """Retrieves a transaction from the database by ID.

        Args:
            id: The ID of the transaction.

        Returns:
            The Transaction object if found, otherwise None.
        """
        with self.Session() as session:
            stmt = db.select(Transaction).where(Transaction.id == id)
            t = session.execute(stmt).scalar()
            if t is None:
                logger.warning(f"No transaction found with id={id}.")
                return None
            else:
                return t

    def select(
        self,
        name: str | None = None,
        amount: float | None = None,
        category: str | None = None,
        date: datetime.date | None = None,
    ) -> list[Transaction]:
        """Searches for transactions matching the provided criteria.

        Args:
            name: Name filter.
            amount: Amount filter.
            category: Category filter.
            date: Date filter.

        Returns:
            A list of matching Transaction objects.
        """
        with self.Session() as session:
            stmt = db.select(Transaction)
            conditions = []

            if name:
                conditions.append(Transaction.name == name)
            if amount is not None:
                conditions.append(Transaction.amount == amount)
            if category:
                conditions.append(Transaction.category == category)
            if date:
                conditions.append(Transaction.date == date)

            if conditions:
                stmt = stmt.where(*conditions)

            results = session.scalars(stmt).all()

            return list(results)

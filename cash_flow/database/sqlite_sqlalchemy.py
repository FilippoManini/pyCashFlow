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
    impl = db.TEXT
    cache_ok = True  # for performance optimization

    def process_bind_param(self, value, dialect) -> str:
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None or value == "":
            return []
        return json.loads(value)


class Base(DeclarativeBase):
    pass


class Transaction(Base):
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
        """Compare two transactions for equality."""
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
        return f"Transaction(id={self.id}, name={self.name}, amount={self.amount}, category={self.category}, date={self.date}, file_paths={self.file_paths})"

    def get_type(self) -> str:
        return "Expense" if self.amount < 0 else "Income"

    def get_file_paths(self) -> str:
        separator = " "
        if self.file_paths != None:
            return separator.join(os.path.basename(path) for path in self.file_paths)
        else:
            return ""


class DBManager:
    def __init__(self, db_name: str = "cashflow"):
        # echo=True for debug
        self.engine = db.create_engine(f"sqlite:///{db_name}.db")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self) -> sessionmaker[Session]:
        return self.Session

    def print_db(self):
        with self.Session() as session:
            stmt = db.select(Transaction)
            transactions = session.scalars(stmt).all()

            for transaction in transactions:
                logger.info(transaction)

    def insert(self, t: Transaction) -> bool:
        with self.Session() as session:
            session.add(t)
            try:
                session.commit()
                return True
            except IntegrityError as e:
                logger.error(f"Insert failed due to exception: {e}")
                return False
            except Exception as e:
                logger.error(f"Insert failed due to exception: {e}")
                return False

    def delete(self, id_to_delete: int) -> bool:
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
        """
        Search for transactions matching the provided fields.
        Each field can be None/empty and will be ignored in the filter.
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

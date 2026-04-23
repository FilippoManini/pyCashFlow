import datetime
import random
import unittest

from cash_flow.database.sqlite_sqlalchemy import DBManager, Transaction


class TestBaseDBManager(unittest.TestCase):
    """base test class for DBManager tests"""

    def setUp(self):
        self.db_manager = DBManager(db_name="test_cashflow")

    def tearDown(self):
        # Clear the test database after each test
        with self.db_manager.Session() as session:
            session.query(Transaction).delete()
            session.commit()

    def test_print_db(self):
        db = DBManager()
        db.print_db()

    def test_create_db(self):
        t = Transaction(
            name="Test",
            amount=10.0,
            category="TestCat",
            date=datetime.date.today(),
            file_paths=[],
        )
        result = self.db_manager.insert(t)
        self.assertTrue(result)

    def test_insert_transaction(self):
        t = Transaction(
            name="Insert",
            amount=20.0,
            category="Cat",
            date=datetime.date.today(),
            file_paths=["home/coop2.pdf", "taxes/coop1.pdf"],
        )
        result = self.db_manager.insert(t)
        self.assertTrue(result)

    def test_insert_transaction_amount_negative(self):
        t = Transaction(
            name="Insert",
            amount=-20.0,
            category="Cat",
            date=datetime.date.today(),
            file_paths=["home/coop2.pdf", "taxes/coop1.pdf"],
        )
        result = self.db_manager.insert(t)
        self.assertTrue(result)

    def test_insert_missing_name(self):
        # Name is required, should fail
        t = Transaction(
            name=None,
            amount=10.0,
            category="TestCat",
            date=datetime.date.today(),
            file_paths=[],
        )
        result = self.db_manager.insert(t)
        self.assertFalse(result)

    def test_insert_missing_amount(self):
        # Amount is required, should fail
        t = Transaction(
            name="Test",
            amount=None,
            category="TestCat",
            date=datetime.date.today(),
            file_paths=[],
        )
        result = self.db_manager.insert(t)
        self.assertFalse(result)

    def test_insert_missing_category(self):
        # Category is required, should fail
        t = Transaction(
            name="Test",
            amount=10.0,
            category=None,
            date=datetime.date.today(),
            file_paths=[],
        )
        result = self.db_manager.insert(t)
        self.assertFalse(result)

    def test_insert_missing_date(self):
        # Date is required, should fail
        t = Transaction(
            name="Test", amount=10.0, category="TestCat", date=None, file_paths=[]
        )
        result = self.db_manager.insert(t)
        self.assertFalse(result)

    def test_insert_invalid_amount_type(self):
        # Amount should be a float, not a string
        t = Transaction(
            name="Test",
            amount="not_a_float",
            category="TestCat",
            date=datetime.date.today(),
            file_paths=[],
        )
        result = self.db_manager.insert(t)
        self.assertFalse(result)

    def test_insert_invalid_file_paths_type(self):
        # file_paths should be a list, not a string
        with self.assertRaises(ValueError):
            t = Transaction(
                name="Test",
                amount=10.0,
                category="TestCat",
                date=datetime.date.today(),
                file_paths="not_a_list",
            )

    def test_delete_transaction(self):
        t = Transaction(
            name="ToDelete",
            amount=40.0,
            category="Cat",
            date=datetime.date.today(),
            file_paths=[],
        )
        self.db_manager.insert(t)
        deleted = self.db_manager.delete(
            1
        )  # Assuming the ID of the inserted transaction is 1
        self.assertTrue(deleted)

    def test_update_transaction(self):
        t = Transaction(
            name="T1",
            amount=30.0,
            category="Cat",
            date=datetime.date.today(),
            file_paths=[],
        )
        self.db_manager.insert(t)
        updated = self.db_manager.update(
            1,
            name="Updated",
            date=datetime.date(2025, 1, 1),
        )
        self.assertTrue(updated)

    def test_select_by_id(self):
        t = Transaction(
            name="ById",
            amount=60.0,
            category="Cat",
            date=datetime.date.today(),
            file_paths=[],
        )
        self.db_manager.insert(t)
        found = self.db_manager.select_id(1)
        self.assertIsNotNone(found)

    def test_select_by_id_not_found(self):
        found = self.db_manager.select_id(2)
        self.assertIsNone(found)

    def test_search_transaction_found(self):
        t1 = Transaction(
            name="Search1",
            amount=50.0,
            category="Cat1",
            date=datetime.date.today(),
            file_paths=[],
        )
        t2 = Transaction(
            name="Search2",
            amount=70.0,
            category="Cat2",
            date=datetime.date.today(),
            file_paths=["file1.pdf"],
        )
        self.db_manager.insert(t1)
        self.db_manager.insert(t2)

        results = self.db_manager.select(name="Search1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Search1")

    def test_search_transaction_not_found(self):
        results = self.db_manager.select(name="NonExistent")
        self.assertEqual(len(results), 0)


class TestRealDBManager(unittest.TestCase):
    """Real database tests for DBManager"""

    def setUp(self):
        self.db_manager = DBManager(db_name="test_cashflow")

    def test_cler_db(self):
        """Clear the database before each test."""
        with self.db_manager.Session() as session:
            session.query(Transaction).delete()
            session.commit()

    def test_insert(self):
        """Simulation of 500 annual transactions for 10 years.
        Performance is not an issue for this test.
        """
        # with self.db_manager.Session() as session:
        #     session.query(Transaction).delete()
        #     session.commit()

        test_file_paths = [[], ["home/coop.pdf"], ["taxes/coop.pdf", "home/coop.pdf"]]
        test_category = [
            "home",
            "taxes",
            "utilities",
            "groceries",
            "entertainment",
            "transportation",
            "healthcare",
            "education",
            "clothing",
            "miscellaneous",
        ]

        with self.db_manager.Session() as session:
            for i in range(5000):
                t = Transaction(
                    name=f"Transaction {i}",
                    amount=round(random.uniform(1, 1000), 2),
                    category=random.choice(test_category),
                    date=datetime.date.today() - datetime.timedelta(days=i),
                    file_paths=random.choice(test_file_paths),
                )
                session.add(t)

            session.commit()

    def test_print_db(self):
        """Print the contents of the database for debugging purposes."""
        self.db_manager.print_db()

    def test_select_1(self):
        results = self.db_manager.select(name="Transaction 1")
        self.assertEqual(len(results), 1)

    def test_select_2500(self):
        results = self.db_manager.select(name="Transaction 2500")
        self.assertEqual(len(results), 1)

    def test_select_4999(self):
        results = self.db_manager.select(name="Transaction 4999")
        self.assertEqual(len(results), 1)

    def test_select_category_home(self):
        results = self.db_manager.select(category="home")
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Found {len(results)} transactions in the 'home' category.")


class TestBigDBManager(unittest.TestCase):
    def setUp(self):
        self.db_manager = DBManager(db_name="test_big_cashflow")

    def test_print_db(self):
        self.db_manager.print_db()

    def test_cler_db(self):
        """Clear the database before each test."""
        with self.db_manager.Session() as session:
            session.query(Transaction).delete()
            session.commit()

    def test_insert(self):

        test_file_paths = [[], ["home/coop.pdf"], ["taxes/coop.pdf", "home/coop.pdf"]]
        test_category = [
            "home",
            "taxes",
            "utilities",
            "groceries",
            "entertainment",
            "transportation",
            "healthcare",
            "education",
            "clothing",
            "miscellaneous",
        ]

        with self.db_manager.Session() as session:
            for i in range(100000):
                t = Transaction(
                    name=f"Transaction {i}",
                    amount=round(random.uniform(1, 1000), 2),
                    category=random.choice(test_category),
                    date=datetime.date.today() - datetime.timedelta(days=i),
                    file_paths=random.choice(test_file_paths),
                )
                session.add(t)

            session.commit()

    def test_select_random(self):
        results = self.db_manager.select(
            name=f"Transaction {random.randint(1, 100000)}"
        )
        import logging

        logger = logging.getLogger(__name__)
        logger.info(results)
        self.assertEqual(len(results), 1)

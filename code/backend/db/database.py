import psycopg2
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from psycopg2.extras import RealDictCursor
from core.logging import get_logger

logger = get_logger(__name__)


class Database:

    def __init__(self) -> Any:
        self.connection = None
        self.cursor = None

    def connect(self) -> Any:
        """Connect to the PostgreSQL database server"""
        try:
            self.connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            logger.info(f"Error connecting to PostgreSQL database: {error}")
            return False

    def disconnect(self) -> Any:
        """Close the database connection"""
        if self.connection:
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None

    def execute_query(self, query: Any, params: Any = None) -> Any:
        """Execute a query and return results"""
        try:
            if not self.connection:
                self.connect()
            self.cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            self.connection.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            logger.info(f"Error executing query: {error}")
            if self.connection:
                self.connection.rollback()
            return None

    def get_portfolio(self, user_address: Any) -> Any:
        """Get portfolio for a specific user"""
        query = "\n        SELECT p.id, p.user_address, p.created_at,\n               a.asset_symbol, a.percentage\n        FROM portfolios p\n        LEFT JOIN allocations a ON p.id = a.portfolio_id\n        WHERE p.user_address = %s\n        "
        return self.execute_query(query, (user_address,))

    def save_portfolio(self, user_address: Any, allocations: Any) -> Any:
        """Save or update portfolio for a user"""
        try:
            if not self.connection:
                self.connect()
            self.cursor.execute(
                "SELECT id FROM portfolios WHERE user_address = %s", (user_address,)
            )
            result = self.cursor.fetchone()
            if result:
                portfolio_id = result["id"]
                self.cursor.execute(
                    "DELETE FROM allocations WHERE portfolio_id = %s", (portfolio_id,)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO portfolios (user_address) VALUES (%s) RETURNING id",
                    (user_address,),
                )
                portfolio_id = self.cursor.fetchone()["id"]
            for asset, percentage in allocations.items():
                self.cursor.execute(
                    "INSERT INTO allocations (portfolio_id, asset_symbol, percentage) VALUES (%s, %s, %s)",
                    (portfolio_id, asset, percentage),
                )
            self.connection.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            logger.info(f"Error saving portfolio: {error}")
            if self.connection:
                self.connection.rollback()
            return False

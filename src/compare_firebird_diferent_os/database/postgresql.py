"""PostgreSQL database connection implementation."""

from typing import Any, Optional

import psycopg2

from . import DatabaseConnection, DatabaseConfig


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL-specific database connection."""
    
    def connect(self) -> Any:
        """Establish PostgreSQL connection."""
        self._connection = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            dbname=self.config.database,
            user=self.config.user,
            password=self.config.password,
            client_encoding=self.config.charset,
        )
        # Set autocommit for monitoring queries
        self._connection.autocommit = True
        self._cursor = self._connection.cursor()
        return self._connection
    
    def execute_query(self, query: str) -> Any:
        """Execute a query and return the cursor."""
        self._cursor.execute(query)
        return self._cursor
    
    def fetchone(self) -> Any:
        """Fetch one row from the cursor."""
        return self._cursor.fetchone()
    
    def get_cursor(self) -> Any:
        """Get a new cursor for separate operations."""
        return self._connection.cursor()
    
    def close(self) -> None:
        """Close the database connection."""
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()
    
    def get_connection_id(self) -> Optional[Any]:
        """Get the current PostgreSQL backend PID."""
        try:
            cur = self.get_cursor()
            cur.execute("SELECT pg_backend_pid()")
            result = cur.fetchone()
            cur.close()
            return result[0] if result else None
        except Exception:
            return None

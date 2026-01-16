"""MariaDB database connection implementation."""

from typing import Any, Optional

import mariadb

from . import DatabaseConnection, DatabaseConfig


class MariaDBConnection(DatabaseConnection):
    """MariaDB-specific database connection."""
    
    def connect(self) -> Any:
        """Establish MariaDB connection."""
        self._connection = mariadb.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
        )
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
        """Get the current MariaDB connection ID."""
        try:
            cur = self.get_cursor()
            cur.execute("SELECT CONNECTION_ID()")
            result = cur.fetchone()
            cur.close()
            return result[0] if result else None
        except Exception:
            return None

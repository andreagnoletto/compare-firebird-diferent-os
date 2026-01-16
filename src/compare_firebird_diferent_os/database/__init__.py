"""
Database abstraction layer for multi-database benchmarking.

This module provides abstract base classes and factory patterns for supporting
multiple SQL databases (Firebird, MySQL, PostgreSQL, MariaDB) across different
operating systems.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DatabaseConfig:
    """Configuration for database connection with multi-DB support."""
    
    db_type: str  # 'firebird', 'mysql', 'postgresql', 'mariadb'
    os_type: str  # 'windows', 'linux'
    name: str     # Display name (e.g., "MySQL on Linux", "Firebird Windows")
    host: str
    port: int
    database: str
    user: str
    password: str
    charset: str = "UTF8"
    
    def __post_init__(self):
        """Validate required fields."""
        self.db_type = self.db_type.lower()
        self.os_type = self.os_type.lower()
        
        if self.db_type not in ('firebird', 'mysql', 'postgresql', 'mariadb'):
            raise ValueError(
                f"Tipo de banco inválido: {self.db_type}. "
                f"Suportados: firebird, mysql, postgresql, mariadb"
            )
        
        if self.os_type not in ('windows', 'linux'):
            raise ValueError(
                f"Tipo de SO inválido: {self.os_type}. Suportados: windows, linux"
            )
        
        missing = []
        for field, value in [
            ("host", self.host),
            ("database", self.database),
            ("user", self.user),
            ("password", self.password),
        ]:
            if not value:
                missing.append(field)
        
        if missing:
            raise ValueError(
                f"Campos ausentes para {self.name}: {', '.join(missing)}"
            )


class DatabaseConnection(ABC):
    """Abstract base class for database connections."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection = None
        self._cursor = None
    
    @abstractmethod
    def connect(self) -> Any:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> Any:
        """Execute a query and return the cursor."""
        pass
    
    @abstractmethod
    def fetchone(self) -> Any:
        """Fetch one row from the cursor."""
        pass
    
    @abstractmethod
    def get_cursor(self) -> Any:
        """Get a new cursor for separate operations."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    def get_connection_id(self) -> Optional[Any]:
        """Get the current connection/session ID."""
        pass
    
    @property
    def connection(self) -> Any:
        """Get the underlying connection object."""
        return self._connection
    
    @property
    def cursor(self) -> Any:
        """Get the main cursor object."""
        return self._cursor


class DatabaseConnectionFactory:
    """Factory for creating database-specific connection instances."""
    
    @staticmethod
    def create(config: DatabaseConfig) -> DatabaseConnection:
        """Create a database connection based on db_type."""
        from .firebird import FirebirdConnection
        from .mysql import MySQLConnection
        from .postgresql import PostgreSQLConnection
        from .mariadb import MariaDBConnection
        
        connections = {
            'firebird': FirebirdConnection,
            'mysql': MySQLConnection,
            'postgresql': PostgreSQLConnection,
            'mariadb': MariaDBConnection,
        }
        
        connection_class = connections.get(config.db_type)
        if not connection_class:
            raise ValueError(
                f"Database type não suportado: {config.db_type}"
            )
        
        return connection_class(config)

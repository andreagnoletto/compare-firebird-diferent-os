"""
Statistics collectors for different database systems.

This module provides abstract base classes and factory patterns for collecting
database-specific performance metrics and execution statistics.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class StatisticsCollector(ABC):
    """Abstract base class for database statistics collection."""
    
    def __init__(self, connection: Any):
        """
        Initialize collector with a database connection.
        
        Args:
            connection: DatabaseConnection instance
        """
        self.connection = connection
        self._stats_before: Optional[Dict[str, Any]] = None
        self._stats_after: Optional[Dict[str, Any]] = None
    
    @abstractmethod
    def get_execution_plan(self, query: str) -> Optional[str]:
        """
        Get the execution plan for a query without executing it.
        
        Args:
            query: SQL query string
            
        Returns:
            Execution plan as string, or None if unavailable
        """
        pass
    
    @abstractmethod
    def capture_before(self) -> None:
        """Capture database statistics before query execution."""
        pass
    
    @abstractmethod
    def capture_after(self) -> None:
        """Capture database statistics after query execution."""
        pass
    
    @abstractmethod
    def get_io_stats(self) -> Dict[str, Any]:
        """
        Get I/O statistics delta between before/after captures.
        
        Returns:
            Dictionary with keys:
                - seq_reads: Sequential/table reads
                - idx_reads: Index reads
                - inserts: Record inserts
                - updates: Record updates
                - deletes: Record deletes
                - (optional DB-specific metrics)
        """
        pass
    
    def reset(self) -> None:
        """Reset captured statistics."""
        self._stats_before = None
        self._stats_after = None


class StatisticsCollectorFactory:
    """Factory for creating database-specific statistics collectors."""
    
    @staticmethod
    def create(db_type: str, connection: Any) -> StatisticsCollector:
        """
        Create a statistics collector based on database type.
        
        Args:
            db_type: Database type ('firebird', 'mysql', 'postgresql', 'mariadb')
            connection: DatabaseConnection instance
            
        Returns:
            StatisticsCollector instance for the specified database
        """
        from .firebird import FirebirdStatsCollector
        from .mysql import MySQLStatsCollector
        from .postgresql import PostgreSQLStatsCollector
        from .mariadb import MariaDBStatsCollector
        
        collectors = {
            'firebird': FirebirdStatsCollector,
            'mysql': MySQLStatsCollector,
            'postgresql': PostgreSQLStatsCollector,
            'mariadb': MariaDBStatsCollector,
        }
        
        collector_class = collectors.get(db_type.lower())
        if not collector_class:
            raise ValueError(
                f"Database type não suportado: {db_type}"
            )
        
        return collector_class(connection)

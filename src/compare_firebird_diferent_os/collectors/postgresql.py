"""PostgreSQL statistics collector implementation."""

import json
from typing import Any, Dict, Optional

from . import StatisticsCollector


class PostgreSQLStatsCollector(StatisticsCollector):
    """PostgreSQL-specific statistics collector using EXPLAIN and pg_stat_* views."""
    
    def get_execution_plan(self, query: str) -> Optional[str]:
        """Get PostgreSQL execution plan using EXPLAIN."""
        try:
            cursor = self.connection.get_cursor()
            cursor.execute(f"EXPLAIN (FORMAT TEXT) {query}")
            rows = cursor.fetchall()
            cursor.close()
            
            if rows:
                # Join all plan lines
                plan_lines = [row[0] for row in rows]
                return " | ".join(plan_lines)
            return None
        except Exception as e:
            return f"Plan error: {str(e)}"
    
    def capture_before(self) -> None:
        """Capture PostgreSQL database statistics before query execution."""
        try:
            cursor = self.connection.get_cursor()
            
            # Get current database name
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            
            # Get database-level statistics
            cursor.execute(f"""
                SELECT 
                    tup_fetched,
                    tup_returned,
                    tup_inserted,
                    tup_updated,
                    tup_deleted,
                    blks_read,
                    blks_hit
                FROM pg_stat_database
                WHERE datname = '{db_name}'
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                self._stats_before = {
                    'tup_fetched': result[0] or 0,
                    'tup_returned': result[1] or 0,
                    'tup_inserted': result[2] or 0,
                    'tup_updated': result[3] or 0,
                    'tup_deleted': result[4] or 0,
                    'blks_read': result[5] or 0,
                    'blks_hit': result[6] or 0,
                }
        except Exception:
            self._stats_before = None
    
    def capture_after(self) -> None:
        """Capture PostgreSQL database statistics after query execution."""
        try:
            cursor = self.connection.get_cursor()
            
            # Get current database name
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            
            # Get database-level statistics
            cursor.execute(f"""
                SELECT 
                    tup_fetched,
                    tup_returned,
                    tup_inserted,
                    tup_updated,
                    tup_deleted,
                    blks_read,
                    blks_hit
                FROM pg_stat_database
                WHERE datname = '{db_name}'
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                self._stats_after = {
                    'tup_fetched': result[0] or 0,
                    'tup_returned': result[1] or 0,
                    'tup_inserted': result[2] or 0,
                    'tup_updated': result[3] or 0,
                    'tup_deleted': result[4] or 0,
                    'blks_read': result[5] or 0,
                    'blks_hit': result[6] or 0,
                }
        except Exception:
            self._stats_after = None
    
    def get_io_stats(self) -> Dict[str, Any]:
        """
        Get I/O statistics delta for PostgreSQL.
        
        Maps PostgreSQL statistics to standard metrics:
        - seq_reads: tup_returned (rows returned, approximates sequential scans)
        - idx_reads: tup_fetched (rows fetched via index)
        - inserts: tup_inserted
        - updates: tup_updated
        - deletes: tup_deleted
        - PostgreSQL-specific: blks_read, blks_hit (buffer cache)
        """
        if not self._stats_before or not self._stats_after:
            return {}
        
        return {
            'seq_reads': (
                self._stats_after['tup_returned'] - 
                self._stats_before['tup_returned']
            ),
            'idx_reads': (
                self._stats_after['tup_fetched'] - 
                self._stats_before['tup_fetched']
            ),
            'inserts': (
                self._stats_after['tup_inserted'] - 
                self._stats_before['tup_inserted']
            ),
            'updates': (
                self._stats_after['tup_updated'] - 
                self._stats_before['tup_updated']
            ),
            'deletes': (
                self._stats_after['tup_deleted'] - 
                self._stats_before['tup_deleted']
            ),
            # PostgreSQL-specific metrics
            'blks_read': (
                self._stats_after['blks_read'] - 
                self._stats_before['blks_read']
            ),
            'blks_hit': (
                self._stats_after['blks_hit'] - 
                self._stats_before['blks_hit']
            ),
        }

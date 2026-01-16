"""MariaDB statistics collector implementation."""

from typing import Any, Dict, Optional

from . import StatisticsCollector


class MariaDBStatsCollector(StatisticsCollector):
    """
    MariaDB-specific statistics collector.
    
    MariaDB uses similar EXPLAIN and SHOW STATUS as MySQL, so we reuse
    the same logic with minor adjustments if needed.
    """
    
    def get_execution_plan(self, query: str) -> Optional[str]:
        """Get MariaDB execution plan using EXPLAIN."""
        try:
            cursor = self.connection.get_cursor()
            cursor.execute(f"EXPLAIN {query}")
            rows = cursor.fetchall()
            cursor.close()
            
            if rows:
                # Format EXPLAIN output as string
                # Columns: id, select_type, table, type, possible_keys, key, key_len, ref, rows, Extra
                plan_lines = []
                for row in rows:
                    plan_lines.append(f"id={row[0]} type={row[3]} table={row[2]} rows={row[8]}")
                return "; ".join(plan_lines)
            return None
        except Exception as e:
            return f"Plan error: {str(e)}"
    
    def capture_before(self) -> None:
        """Capture MariaDB Handler statistics before query execution."""
        try:
            cursor = self.connection.get_cursor()
            cursor.execute("""
                SHOW STATUS LIKE 'Handler_%'
            """)
            results = cursor.fetchall()
            cursor.close()
            
            stats = {}
            for name, value in results:
                try:
                    stats[name] = int(value)
                except (ValueError, TypeError):
                    stats[name] = 0
            
            self._stats_before = {
                'handler_read_rnd_next': stats.get('Handler_read_rnd_next', 0),
                'handler_read_key': stats.get('Handler_read_key', 0),
                'handler_read_next': stats.get('Handler_read_next', 0),
                'handler_write': stats.get('Handler_write', 0),
                'handler_update': stats.get('Handler_update', 0),
                'handler_delete': stats.get('Handler_delete', 0),
            }
        except Exception:
            self._stats_before = None
    
    def capture_after(self) -> None:
        """Capture MariaDB Handler statistics after query execution."""
        try:
            cursor = self.connection.get_cursor()
            cursor.execute("""
                SHOW STATUS LIKE 'Handler_%'
            """)
            results = cursor.fetchall()
            cursor.close()
            
            stats = {}
            for name, value in results:
                try:
                    stats[name] = int(value)
                except (ValueError, TypeError):
                    stats[name] = 0
            
            self._stats_after = {
                'handler_read_rnd_next': stats.get('Handler_read_rnd_next', 0),
                'handler_read_key': stats.get('Handler_read_key', 0),
                'handler_read_next': stats.get('Handler_read_next', 0),
                'handler_write': stats.get('Handler_write', 0),
                'handler_update': stats.get('Handler_update', 0),
                'handler_delete': stats.get('Handler_delete', 0),
            }
        except Exception:
            self._stats_after = None
    
    def get_io_stats(self) -> Dict[str, Any]:
        """
        Get I/O statistics delta for MariaDB.
        
        Maps MariaDB Handler counters to standard metrics (same as MySQL):
        - seq_reads: Handler_read_rnd_next (sequential table scans)
        - idx_reads: Handler_read_key + Handler_read_next (index operations)
        - inserts: Handler_write
        - updates: Handler_update
        - deletes: Handler_delete
        """
        if not self._stats_before or not self._stats_after:
            return {}
        
        return {
            'seq_reads': (
                self._stats_after['handler_read_rnd_next'] - 
                self._stats_before['handler_read_rnd_next']
            ),
            'idx_reads': (
                (self._stats_after['handler_read_key'] - self._stats_before['handler_read_key']) +
                (self._stats_after['handler_read_next'] - self._stats_before['handler_read_next'])
            ),
            'inserts': (
                self._stats_after['handler_write'] - 
                self._stats_before['handler_write']
            ),
            'updates': (
                self._stats_after['handler_update'] - 
                self._stats_before['handler_update']
            ),
            'deletes': (
                self._stats_after['handler_delete'] - 
                self._stats_before['handler_delete']
            ),
        }

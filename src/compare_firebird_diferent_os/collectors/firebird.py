"""Firebird statistics collector implementation."""

from typing import Any, Dict, Optional

from . import StatisticsCollector


class FirebirdStatsCollector(StatisticsCollector):
    """Firebird-specific statistics collector using MON$ tables."""
    
    def get_execution_plan(self, query: str) -> Optional[str]:
        """Get Firebird execution plan using SET PLANONLY."""
        try:
            cursor = self.connection.cursor
            cursor.execute("SET PLANONLY")
            cursor.execute(query)
            plan = cursor.plan if hasattr(cursor, 'plan') else None
            cursor.execute("SET PLANONLY OFF")
            return plan
        except Exception as e:
            return f"Plan error: {str(e)}"
    
    def capture_before(self) -> None:
        """Capture Firebird MON$ statistics before query execution."""
        try:
            attachment_id = self.connection.get_connection_id()
            if not attachment_id:
                self._stats_before = None
                return
            
            cursor = self.connection.get_cursor()
            cursor.execute(f"""
                SELECT 
                    SUM(MON$RECORD_SEQ_READS) as SEQ_READS,
                    SUM(MON$RECORD_IDX_READS) as IDX_READS,
                    SUM(MON$RECORD_INSERTS) as INSERTS,
                    SUM(MON$RECORD_UPDATES) as UPDATES,
                    SUM(MON$RECORD_DELETES) as DELETES,
                    SUM(MON$RECORD_BACKOUTS) as BACKOUTS,
                    SUM(MON$RECORD_PURGES) as PURGES,
                    SUM(MON$RECORD_EXPUNGES) as EXPUNGES
                FROM MON$IO_STATS
                WHERE MON$STAT_GROUP = 1 
                AND MON$STAT_ID = {attachment_id}
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                self._stats_before = {
                    'seq_reads': result[0] or 0,
                    'idx_reads': result[1] or 0,
                    'inserts': result[2] or 0,
                    'updates': result[3] or 0,
                    'deletes': result[4] or 0,
                    'backouts': result[5] or 0,
                    'purges': result[6] or 0,
                    'expunges': result[7] or 0,
                }
        except Exception:
            self._stats_before = None
    
    def capture_after(self) -> None:
        """Capture Firebird MON$ statistics after query execution."""
        try:
            attachment_id = self.connection.get_connection_id()
            if not attachment_id:
                self._stats_after = None
                return
            
            cursor = self.connection.get_cursor()
            cursor.execute(f"""
                SELECT 
                    SUM(MON$RECORD_SEQ_READS) as SEQ_READS,
                    SUM(MON$RECORD_IDX_READS) as IDX_READS,
                    SUM(MON$RECORD_INSERTS) as INSERTS,
                    SUM(MON$RECORD_UPDATES) as UPDATES,
                    SUM(MON$RECORD_DELETES) as DELETES,
                    SUM(MON$RECORD_BACKOUTS) as BACKOUTS,
                    SUM(MON$RECORD_PURGES) as PURGES,
                    SUM(MON$RECORD_EXPUNGES) as EXPUNGES
                FROM MON$IO_STATS
                WHERE MON$STAT_GROUP = 1 
                AND MON$STAT_ID = {attachment_id}
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                self._stats_after = {
                    'seq_reads': result[0] or 0,
                    'idx_reads': result[1] or 0,
                    'inserts': result[2] or 0,
                    'updates': result[3] or 0,
                    'deletes': result[4] or 0,
                    'backouts': result[5] or 0,
                    'purges': result[6] or 0,
                    'expunges': result[7] or 0,
                }
        except Exception:
            self._stats_after = None
    
    def get_io_stats(self) -> Dict[str, Any]:
        """Get I/O statistics delta for Firebird."""
        if not self._stats_before or not self._stats_after:
            return {}
        
        return {
            'seq_reads': self._stats_after['seq_reads'] - self._stats_before['seq_reads'],
            'idx_reads': self._stats_after['idx_reads'] - self._stats_before['idx_reads'],
            'inserts': self._stats_after['inserts'] - self._stats_before['inserts'],
            'updates': self._stats_after['updates'] - self._stats_before['updates'],
            'deletes': self._stats_after['deletes'] - self._stats_before['deletes'],
            # Firebird-specific metrics
            'backouts': self._stats_after['backouts'] - self._stats_before['backouts'],
            'purges': self._stats_after['purges'] - self._stats_before['purges'],
            'expunges': self._stats_after['expunges'] - self._stats_before['expunges'],
        }

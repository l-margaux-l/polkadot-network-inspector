from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, select
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.pool import StaticPool

from models.metrics import HealthMetrics
from config import DB_DIR


Base = declarative_base()


class MetricsRecord(Base):
    """SQLAlchemy ORM model for storing metrics in SQLite."""
    
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    node_name = Column(String(255), nullable=False, index=True)
    block_height = Column(Integer, nullable=False)
    current_block_height = Column(Integer, nullable=False)
    peers_count = Column(Integer, nullable=False)
    finality_lag = Column(Integer, nullable=False)
    time_since_last_block = Column(Integer, nullable=False)
    rpc_response_time = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)


class MetricsDB:
    """Database interface for metrics storage and retrieval."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path is None:
            db_path = str(DB_DIR / "inspector.db")
        
        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    
    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    def insert_metrics(self, metrics: HealthMetrics) -> None:
        """Insert a single metrics record into database."""
        record = MetricsRecord(
            timestamp=metrics.timestamp,
            node_name=metrics.node_name,
            block_height=metrics.block_height,
            current_block_height=metrics.current_block_height,
            peers_count=metrics.peers_count,
            finality_lag=metrics.finality_lag,
            time_since_last_block=metrics.time_since_last_block,
            rpc_response_time=metrics.rpc_response_time,
            status=metrics.status,
        )
        
        with Session(self.engine) as session:
            session.add(record)
            session.commit()
    
    def insert_batch(self, metrics_list: List[HealthMetrics]) -> None:
        """Insert multiple metrics records in a single transaction."""
        records = [
            MetricsRecord(
                timestamp=m.timestamp,
                node_name=m.node_name,
                block_height=m.block_height,
                current_block_height=m.current_block_height,
                peers_count=m.peers_count,
                finality_lag=m.finality_lag,
                time_since_last_block=m.time_since_last_block,
                rpc_response_time=m.rpc_response_time,
                status=m.status,
            )
            for m in metrics_list
        ]
        
        with Session(self.engine) as session:
            session.add_all(records)
            session.commit()
    
    def get_metrics_for_node(
        self,
        node_name: str,
        hours: int = 24
    ) -> List[HealthMetrics]:
        """Retrieve metrics for a specific node within the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with Session(self.engine) as session:
            stmt = select(MetricsRecord).where(
                (MetricsRecord.node_name == node_name) &
                (MetricsRecord.timestamp >= cutoff_time)
            ).order_by(MetricsRecord.timestamp.desc())
            
            records = session.execute(stmt).scalars().all()
            
            return [
                HealthMetrics(
                    timestamp=r.timestamp,
                    node_name=r.node_name,
                    block_height=r.block_height,
                    current_block_height=r.current_block_height,
                    peers_count=r.peers_count,
                    finality_lag=r.finality_lag,
                    time_since_last_block=r.time_since_last_block,
                    rpc_response_time=r.rpc_response_time,
                    status=r.status,
                )
                for r in records
            ]
    
    def get_latest_for_node(self, node_name: str) -> Optional[HealthMetrics]:
        """Retrieve the most recent metric record for a node."""
        with Session(self.engine) as session:
            stmt = select(MetricsRecord).where(
                MetricsRecord.node_name == node_name
            ).order_by(MetricsRecord.timestamp.desc()).limit(1)
            
            record = session.execute(stmt).scalar_one_or_none()
            
            if record is None:
                return None
            
            return HealthMetrics(
                timestamp=record.timestamp,
                node_name=record.node_name,
                block_height=record.block_height,
                current_block_height=record.current_block_height,
                peers_count=record.peers_count,
                finality_lag=record.finality_lag,
                time_since_last_block=record.time_since_last_block,
                rpc_response_time=record.rpc_response_time,
                status=record.status,
            )
    
    def get_all_nodes(self) -> List[str]:
        """Get list of all unique nodes in database."""
        with Session(self.engine) as session:
            stmt = select(MetricsRecord.node_name).distinct()
            nodes = session.execute(stmt).scalars().all()
            return list(nodes)
    
    def count_records(self, node_name: Optional[str] = None) -> int:
        """Count total records or records for specific node."""
        with Session(self.engine) as session:
            if node_name:
                stmt = select(MetricsRecord).where(
                    MetricsRecord.node_name == node_name
                )
            else:
                stmt = select(MetricsRecord)
            
            count = session.query(MetricsRecord).count() if not node_name else \
                    session.query(MetricsRecord).filter(
                        MetricsRecord.node_name == node_name
                    ).count()
            return count

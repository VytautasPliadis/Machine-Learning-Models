from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Type, List

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.metals_api.metals_api import MetalsData
from src.db_api.sqlalchemy_model import AnalyticsData
from src.utils.logger import logger


class DatabaseManager:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self) -> None:
        from src.db_api.sqlalchemy_model import Base

        Base.metadata.create_all(bind=self.engine)
        logger.info("Tables created if not existed")

    @contextmanager
    def get_db_session(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        db_session = self.SessionLocal()
        try:
            yield db_session
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            db_session.rollback()
        finally:
            db_session.close()

    def create_view(self, view_name: str, base_table: str) -> None:
        # Drop the view if it exists
        with self.get_db_session() as session:
            drop_view_sql = text(f"DROP VIEW IF EXISTS {view_name};")
            session.execute(drop_view_sql)
            session.commit()

        # Create the view
        with self.get_db_session() as session:
            try:
                create_view_sql = text(
                    f"""
                                            CREATE VIEW {view_name} AS
                                            SELECT * 
                                            FROM {base_table}
                                            WHERE timestamp >= NOW() - INTERVAL '12 hours';
                                            """
                )
                session.execute(create_view_sql)
                session.commit()
                logger.info(f"View {view_name} created successfully.")

            except Exception as e:
                logger.error(f"An error occurred while creating view {view_name}: {e}")
                raise

    def insert_records_from_tuple(
        self, model: Type[AnalyticsData], data: MetalsData
    ) -> None:
        """Insert records into the database."""
        with self.get_db_session() as session:
            try:
                datetime_timestamp = datetime.fromtimestamp(
                    data.timestamp, timezone.utc
                )
                record = model(
                    timestamp=datetime_timestamp,
                    xauusd=data.xauusd,
                    xagusd=data.xagusd,
                    xptusd=data.xptusd,
                    xpdusd=data.xpdusd,
                )

                session.add(record)
                session.commit()
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                raise

    def get_data_for_ticker(self, ticker: str) -> List[float]:
        query_sql = text(
            f"""
                            SELECT {ticker} 
                            FROM ml_train_data 
                            WHERE {ticker} IS NOT NULL
                            ORDER BY timestamp DESC;
                            """
        )
        with self.get_db_session() as session:
            try:
                result = session.execute(query_sql)
                return [row[0] for row in result.fetchall()]
            except Exception as e:
                logger.error(
                    f"An error occurred while retrieving data for {ticker}: {e}"
                )
                raise

from sqlalchemy import Column, Integer, TIMESTAMP, DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AnalyticsData(Base):
    __tablename__ = "analytics_data"
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP)
    xagusd = Column(DECIMAL(10, 2))
    xauusd = Column(DECIMAL(10, 2))
    xpdusd = Column(DECIMAL(10, 2))
    xptusd = Column(DECIMAL(10, 2))

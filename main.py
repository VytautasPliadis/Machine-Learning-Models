import asyncio
from typing import Optional

from config import API_KEY, DATABASE_URL
from src.db_api.database_manager import DatabaseManager
from src.db_api.sqlalchemy_model import AnalyticsData
from src.metals_api.metals_api import AsyncAPIClient, MetalsData
from src.model.model import Model
from src.utils.logger import logger


async def fetch_data(client: AsyncAPIClient) -> Optional[MetalsData]:
    """Fetches data from the API."""
    try:
        data = await client.fetch_data(
            f"?api_key={API_KEY}&base=USD&currencies=XAU,XAG,XPT,XPD"
        )
        logger.info(f"Fetched data: {data}")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return None


def upload_to_database(data: MetalsData, db: DatabaseManager) -> None:
    """Uploads fetched data to the database."""
    db.create_tables()
    db.create_view("ml_train_data", "analytics_data")
    db.insert_records_from_tuple(AnalyticsData, data)


def train_and_save_models(db: DatabaseManager) -> None:
    """Trains and saves the model."""
    try:
        model = Model(["xauusd", "xagusd", "xptusd", "xpdusd"], 12, 1, db)
        model.train(use_generated_data=False)
        model.save("model1")
        logger.info("Models trained and saved successfully.")
    except Exception as e:
        logger.error(f"Failed to train or save models: {e}")


async def main() -> None:
    db = DatabaseManager(DATABASE_URL)
    client = AsyncAPIClient("https://api.metalpriceapi.com/v1/latest")
    data = await fetch_data(client)

    if data:
        upload_to_database(data, db)
        train_and_save_models(db)


if __name__ == "__main__":
    asyncio.run(main())

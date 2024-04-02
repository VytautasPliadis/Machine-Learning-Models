from dataclasses import dataclass
from typing import Optional

import aiohttp

from src.utils.logger import logger


@dataclass
class MetalsData:
    timestamp: int
    xauusd: float
    xagusd: float
    xptusd: float
    xpdusd: float


class AsyncAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    async def fetch_data(self, endpoint: str) -> Optional[MetalsData]:
        """Asynchronously fetch data from a specified endpoint of the API."""
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data.get("success"):
                        for key, value in data["rates"].items():
                            # Update the rate to eur
                            rates = {
                                k: round((1 / v), 2) for k, v in data["rates"].items()
                            }
                            return MetalsData(
                                timestamp=data["timestamp"],
                                xauusd=rates["XAU"],
                                xagusd=rates["XAG"],
                                xptusd=rates["XPT"],
                                xpdusd=rates["XPD"],
                            )

            except aiohttp.ClientError as e:
                logger.error(f"An error occurred: {e}")
                return None

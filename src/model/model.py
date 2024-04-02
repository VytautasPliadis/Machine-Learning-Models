from __future__ import annotations

from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sktime.forecasting.arima import ARIMA
from sktime.forecasting.base import ForecastingHorizon

from src.db_api.database_manager import DatabaseManager
from src.utils.logger import logger

rng = np.random.default_rng()

AR_LOWER = 0.1
AR_UPPER = 0.6
MEAN_LOWER = 1000
MEAN_UPPER = 2000
STD = 1


def generate_integrated_autocorrelated_series(
    p: float, mean: float, std: float, length: int
) -> np.ndarray:
    """Generates an integrated autocorrelated time series using a specified autoregression parameter,
    mean and standard deviation of the normal distribution, and the desired length of the series.
    """
    x = 0
    ar1_series = np.asarray([x := p * x + rng.normal(0, 1) for _ in range(length)])
    return np.cumsum(ar1_series * std) + mean


def generate_sample_data(
    cols: list[str], x_size: int, y_size: int
) -> tuple[pd.DataFrame, pd.DataFrame, tuple[np.ndarray, np.ndarray]]:
    """Generates sample training and test data for specified columns. The data consists of autocorrelated series,
    each created with randomly generated autoregression coefficients and means. The method also returns the generated
    autocorrelation coefficients and means for reference. 'x_size' determines the length of the training set,
    and 'y_size' determines the length of the test set. 'cols' determines the names of the columns.
    """
    ar_coefficients = rng.uniform(AR_LOWER, AR_UPPER, len(cols))
    means = rng.uniform(MEAN_LOWER, MEAN_UPPER, len(cols))
    full_dataset = pd.DataFrame.from_dict(
        {
            col_name: generate_integrated_autocorrelated_series(
                ar_coefficient, mean, STD, x_size + y_size
            )
            for ar_coefficient, mean, col_name in zip(ar_coefficients, means, cols)
        }
    )
    return (
        full_dataset.head(x_size),
        full_dataset.tail(y_size),
        (ar_coefficients, means),
    )


class Model:
    def __init__(
        self, tickers: list[str], x_size: int, y_size: int, db_manager: DatabaseManager
    ) -> None:
        self.tickers = tickers
        self.x_size = x_size
        self.y_size = y_size
        self.models: dict[str, ARIMA] = {}
        self.db_manager = db_manager
        self.model_creation_day = datetime.now().strftime("%Y-%m-%d")
        self.predictions = {}

    def train(self, /, use_generated_data: bool = False) -> None:
        if use_generated_data:
            data, _, _ = generate_sample_data(self.tickers, self.x_size, self.y_size)
        else:
            data = pd.DataFrame()
            for ticker in self.tickers:
                # Fetch data from the database for each ticker
                dataset = self.db_manager.get_data_for_ticker(ticker)
                data[ticker] = dataset

        for ticker in self.tickers:
            dataset = data[ticker].values.astype(float)
            model = ARIMA(order=(1, 1, 0), with_intercept=True, suppress_warnings=True)
            model.fit(dataset)
            self.models[ticker] = model

    def save(self, path_to_dir: str | Path) -> None:
        path_to_dir = Path(path_to_dir)
        path_to_dir.mkdir(parents=True, exist_ok=True)
        for ticker, model in self.models.items():
            full_path = path_to_dir / f"{ticker}.joblib"
            joblib.dump(model, full_path)
            logger.info(f"{ticker} model saved!")

    def load(self, path_to_dir: str | Path) -> None:
        """Loads models for each ticker from the specified directory."""
        path_to_dir = Path(path_to_dir)
        for ticker in self.tickers:
            full_path = path_to_dir / f"{ticker}.joblib"
            if full_path.exists():
                self.models[ticker] = joblib.load(full_path)
            else:
                logger.info(f"Model for {ticker} not found in {path_to_dir}.")

    def predict(self, steps_ahead: int) -> dict:
        predicted_values = {}
        for ticker in self.tickers:
            if ticker not in self.models:
                raise ValueError(f"No model found for ticker {ticker}.")

            # Retrieve the specific ARIMA model for the ticker
            arima_model = self.models[ticker]

            # Create a forecasting horizon from 1 to steps_ahead
            fh = ForecastingHorizon(np.arange(1, steps_ahead + 1), is_relative=True)

            # Predict the future values using the ARIMA model
            rounded_arr = np.round(arima_model.predict(fh=fh), 2)
            floats_list = [float(x) for x in rounded_arr]
            predicted_values[ticker] = floats_list
        return predicted_values

from config import DATABASE_URL
from src.db_api.database_manager import DatabaseManager
from src.model.model import Model
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

db = DatabaseManager(DATABASE_URL)
model_path = Path("model1")
model = Model(["xauusd", "xagusd", "xptusd", "xpdusd"], 12, 1, db)
model.load(model_path)


class PredictionRequest(BaseModel):
    tickers: List[str] = ["xauusd", "xagusd", "xptusd", "xpdusd"]
    steps_ahead: int = 1


class PredictionResponse(BaseModel):
    predictions: dict


@app.post("/predict/", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        predictions = model.predict(steps_ahead=request.steps_ahead)
        filtered_predictions = {
            ticker: predictions[ticker] for ticker in request.tickers
        }
        return PredictionResponse(predictions=filtered_predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from forecast_plugin.model import ForecastModel

app = FastAPI()
model = ForecastModel()

@app.get("/forecast")
def get_forecast(steps: int = 1):
    """
    Restituisce la previsione delle risorse per N step futuri.
    Parametri:
    - steps: numero di intervalli futuri da prevedere (default = 1)
    """
    return model.forecast(steps_ahead=steps)

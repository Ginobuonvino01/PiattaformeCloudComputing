import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

class ForecastModel:
    def __init__(self, csv_path="forecast_plugin/data/metrics.csv"):
        self.data = pd.read_csv(csv_path)
        self.model_cpu = LinearRegression()
        self.model_ram = LinearRegression()
        self.model_storage = LinearRegression()
        self._train()

    def _train(self):
        # Converti timestamp in indice numerico
        X = np.arange(len(self.data)).reshape(-1, 1)
        y_cpu = self.data["cpu_usage"].values
        y_ram = self.data["ram_usage"].values
        y_storage = self.data["storage_usage"].values

        self.model_cpu.fit(X, y_cpu)
        self.model_ram.fit(X, y_ram)
        self.model_storage.fit(X, y_storage)

    def forecast(self, steps_ahead=1):
        next_index = np.array([[len(self.data) + steps_ahead - 1]])
        return {
            "cpu_forecast": round(float(self.model_cpu.predict(next_index)), 2),
            "ram_forecast": round(float(self.model_ram.predict(next_index)), 2),
            "storage_forecast": round(float(self.model_storage.predict(next_index)), 2)
        }

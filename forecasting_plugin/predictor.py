import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings('ignore')


class ResourcePredictor:
    def __init__(self, historical_data=None):
        self.historical_data = historical_data or []

    def simple_linear_regression(self, data_points, forecast_hours=24):
        """Regressione lineare semplice"""
        if len(data_points) < 2:
            return None

        X = np.array(range(len(data_points))).reshape(-1, 1)
        y = np.array(data_points)

        model = LinearRegression()
        model.fit(X, y)

        # Previsione per le prossime N ore
        future_X = np.array(range(len(data_points),
                                  len(data_points) + forecast_hours)).reshape(-1, 1)
        predictions = model.predict(future_X)

        return predictions.tolist()

    def moving_average(self, data_points, window=6):
        """Media mobile per smoothing"""
        if len(data_points) < window:
            return data_points

        series = pd.Series(data_points)
        return series.rolling(window=window).mean().dropna().tolist()

    def predict_resource_usage(self, metric_type, historical_values, method='linear'):
        """Predice l'uso futuro delle risorse"""
        if method == 'linear':
            return self.simple_linear_regression(historical_values)
        elif method == 'arima':
            # Implementazione base ARIMA
            try:
                model = ARIMA(historical_values, order=(1, 1, 1))
                model_fit = model.fit()
                forecast = model_fit.forecast(steps=24)
                return forecast.tolist()
            except:
                return self.simple_linear_regression(historical_values)
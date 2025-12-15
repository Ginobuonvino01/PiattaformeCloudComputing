import numpy as np


class ResourcePredictor:
    def simple_linear_regression(self, data_points, forecast_hours=24):
        """Regressione lineare semplice usando solo numpy"""
        if len(data_points) < 2:
            return [data_points[-1]] * forecast_hours if data_points else [50] * forecast_hours

        x = np.arange(len(data_points))
        y = np.array(data_points)

        # Calcolo manuale regressione lineare
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x * x)

        #Formula
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return [np.mean(y)] * forecast_hours #Se divisione per zero

        m = (n * sum_xy - sum_x * sum_y) / denominator #Pendenza
        b = (sum_y - m * sum_x) / n #Intercetta

        #Calcolo previsioni future
        future_x = np.arange(n, n + forecast_hours)
        predictions = m * future_x + b

        # Clip tra 0 e 100 per percentuali
        predictions = np.clip(predictions, 0, 100)

        return predictions.tolist()
import numpy as np
from datetime import datetime
import random

class ResourcePredictor:
    def sinusoidal_with_trend(self, data_points, forecast_hours=24):
        """Modello sinusoidale"""
        if len(data_points) < 4:
            # Se non abbiamo abbastanza dati, usiamo pattern giornaliero di default
            return self.default_daily_pattern(forecast_hours, data_points[-1] if data_points else 15)

        # Prendi l'ultimo valore misurato
        current_value = data_points[-1] if data_points else 15

        # Calcola una media mobile degli ultimi valori
        recent_data = data_points[-min(24, len(data_points)):]  # prendi 24 , ma se hai meno di 24 dati prendi tutti quelli che hai
        base_value = np.mean(recent_data) if recent_data else current_value #Media degli ultimi dati

        # Calcola un trend molto leggero (almeno 2 punti per capire la pendenza)
        if len(data_points) >= 2:
            last_values = data_points[-min(6, len(data_points)):]  # Prendo gli ultimi valori al massimo 6
            #controllo anche gli elementi di last values per sicurezza
            if len(last_values) >= 2:
                # Calcola pendenza basata sugli ultimi valori
                x = np.arange(len(last_values)) #x=[0,1,2,3]
                y = np.array(last_values) #y=[20,21,22,23]

                # Regressione lineare semplice (in maniera da trovare la retta che meglio si adatta ai punti)
                A = np.vstack([x, np.ones(len(x))]).T
                m, c = np.linalg.lstsq(A, y, rcond=None)[0]
                trend_slope = m
            else:
                trend_slope = 0 #se non ci sono abbastanza dati trend = 0
        else:
            trend_slope = 0

        # Limita la pendenza a valori realistici (max ±2% per ora)
        trend_slope = max(-2.0, min(2.0, trend_slope))

        hour_now = datetime.now().hour #ora attuale
        predictions = [] #lista per mettere previsioni

        #iterazione per ogni ora
        for i in range(forecast_hours):
            hour_of_day = (hour_now + i) % 24 #Calcola che ora sarà quando questa previsione si realizzerà

            # COMPONENTE BASE: valore attuale + trend leggero
            base_component = current_value + (trend_slope * i)

            # COMPONENTE SINUSOIDALE: pattern giornaliero realistico
            # Picco alle 14-16, minimo alle 4-6
            # Ampiezza in base al valore base (non fissa!)

            # Normalizza il valore base per determinare l'ampiezza
            amplitude = 0.4 * base_value  # 40% del valore base come ampiezza (come oscillano le onde)

            # Calcola fase per picco alle 14 (2 PM)
            phase_shift = 14  # Picco alle 14:00

            # Funzione sinusoidale normalizzata
            sine_value = amplitude * np.sin(2 * np.pi * (hour_of_day - phase_shift) / 24)

            # COMBINA le componenti
            prediction = base_component + sine_value #Somma la linea di tendenza con l'onda sinusoidale

            # Aggiungi piccola variazione random (non più del ±5%)
            random_variation = random.uniform(-min(5, prediction * 0.3), min(5, prediction * 0.3))
            prediction += random_variation

            # La previsione deve essere ragionevole rispetto al valore attuale
            # Non può crescere/decrescere troppo in poche ore
            max_change_per_hour = 0.3 * current_value  # Max 30% del valore attuale per ora
            if i > 0:
                previous_pred = predictions[-1]
                if abs(prediction - previous_pred) > max_change_per_hour:
                    # Limita il cambio
                    if prediction > previous_pred:
                        prediction = previous_pred + max_change_per_hour
                    else:
                        prediction = previous_pred - max_change_per_hour

            # Limita tra 0 e 100%
            prediction = max(0.0, min(100.0, prediction))

            # Arrotondamento
            predictions.append(round(prediction, 1))

        return predictions

    def default_daily_pattern(self, forecast_hours, current_value=15):
        """Pattern giornaliero realistico basato sul valore attuale"""
        hour_now = datetime.now().hour
        predictions = []

        for i in range(forecast_hours):
            hour_of_day = (hour_now + i) % 24

            # Pattern realistico basato su studi di carico cloud
            # I valori sono percentuali rispetto al valore attuale

            if 0 <= hour_of_day < 6:  # Notte profonda (0-6)
                factor = 0.6  # -40%
            elif 6 <= hour_of_day < 9:  # Mattina presto (6-9)
                factor = 0.8  # -20%
            elif 9 <= hour_of_day < 12:  # Mattina lavorativa (9-12)
                factor = 1.2  # +20%
            elif 12 <= hour_of_day < 14:  # Pausa pranzo (12-14)
                factor = 1.0  # Valore base
            elif 14 <= hour_of_day < 18:  # Pomeriggio lavorativo (14-18)
                factor = 1.4  # +40% (picco)
            elif 18 <= hour_of_day < 22:  # Sera (18-22)
                factor = 0.9  # -10%
            else:  # Notte (22-24)
                factor = 0.7  # -30%

            # Calcola predizione
            prediction = current_value * factor

            # Aggiungi piccola variazione random
            prediction += random.uniform(-3, 3)

            # Limita valori
            prediction = max(5.0, min(95.0, prediction))

            predictions.append(round(prediction, 1))

        return predictions

    # Vecchio metodo per compatibilità (non utilizzato più nelle API)
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

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return [np.mean(y)] * forecast_hours

        m = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - m * sum_x) / n

        future_x = np.arange(n, n + forecast_hours)
        predictions = m * future_x + b

        # Clip tra 0 e 100 per percentuali
        predictions = np.clip(predictions, 0, 100)

        return predictions.tolist()
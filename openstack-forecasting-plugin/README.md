# AI Resource Forecasting for OpenStack (Nova/Cinder)

## Descrizione

Questo progetto implementa un servizio dimostrativo di **previsione delle risorse** per un ambiente OpenStack.
L'obiettivo è:

- raccogliere metriche di utilizzo (CPU, RAM, storage),
- applicare un modello di **regressione lineare** semplice,
- esporre un **endpoint REST** che fornisce:
  - la previsione del prossimo valore,
  - eventuali *alert* se si superano soglie predefinite.

Non viene implementato alcun meccanismo di autoscaling: il focus è sulla parte di forecasting e sull'integrazione con OpenStack.

## Architettura

- **Collectors**: modulo che raccoglie le metriche
  - `mock_collector.py`: genera metriche finte per test locale.
  - `nova_collector.py`: usa le API OpenStack (Nova, Cinder) per ottenere dati reali.
- **Models**: contiene il modello di previsione
  - `linear_forecaster.py`: implementa una regressione lineare per predire il prossimo punto di una serie temporale.
- **API**:
  - `api/main.py`: applicazione FastAPI che espone gli endpoint REST.
- **Config**:
  - `config.py`: gestisce impostazioni come la modalità (`mock` vs `openstack`) e le soglie di alert.

## Endpoint principali

- `GET /forecast`
  - Restituisce per ogni risorsa (CPU, RAM, storage):
    - serie storica (`history`),
    - previsione del prossimo valore (`next_prediction`).

- `GET /forecast/alerts`
  - Calcola la previsione e verifica se supera soglie definite in `config.py`.
  - Restituisce, per ogni risorsa:
    - valore previsto,
    - soglia,
    - flag `alert` (true/false).

## Modalità operative

### Modalità mock (sviluppo locale)

1. Assicurarsi che in `config.py` o nel file `.env` sia impostato:
   ```text
   metrics_mode=mock

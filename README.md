# OpenStack Resource Forecasting Plugin

**Monitoraggio e previsioni intelligenti per risorse OpenStack DevStack**

📋 **Descrizione**  
Un plugin intelligente per OpenStack DevStack che monitora e prevede l'utilizzo delle risorse cloud in tempo reale, fornendo analisi predittive basate su variabili come l'uso di CPU e RAM delle VM.

💡 **Soluzione Innovativa**  
Il plugin utilizza un approccio intelligente per il calcolo delle metriche, tra cui:

- **VM ACTIVE/SHUTOFF**: rilevamento automatico degli stati delle VM.
- **Flavor analysis**: calcolo delle risorse basato sui flavor delle VM.
- **Pattern realistici**: simulazione di variazioni giornaliere delle risorse.
- **Regressione lineare**: forecasting automatico basato sui dati storici.

🚀 **Caratteristiche**  
✅ **Funzionalità Completa**:

- **Collector Intelligente**: scansione automatica ogni 60 secondi delle VM OpenStack.
- **Rilevamento Stati VM**: distingue tra VM ACTIVE e SHUTOFF, calcolando le risorse allocate.
- **Metriche Realistiche**: CPU e RAM proporzionali al numero di VM attive.
- **Forecasting Dinamico**: regressione lineare che si adatta ai cambiamenti in tempo reale.
- **API REST Completa**: 5 endpoint documentati per integrare facilmente il sistema.
- **Sistema di Alert**: soglie configurabili per CPU/RAM per monitorare le risorse.
- **Integrazione con DevStack**: plugin ufficiale per l'installazione su DevStack.

📡 **Endpoint API**  
| Endpoint                         | Metodo | Descrizione                                    | Output                               |
| --------------------------------- | ------ | ---------------------------------------------- | ------------------------------------ |
| `/api/v1/health`                 | GET    | Stato del servizio e metriche live             | JSON con health status               |
| `/api/v1/metrics/current`        | GET    | Metriche correnti (CPU, RAM)                   | Valori percentuali                   |
| `/api/v1/forecast/cpu?hours=12`  | GET    | Previsioni CPU per N ore                       | Array di predizioni                  |
| `/api/v1/alerts`                 | GET    | Alert attivi (soglie superate)                 | Lista alert con severità             |
| `/api/v1/openstack/info`         | GET    | Info dettagliate OpenStack                     | Server, hypervisor, risorse         |

# 📦 Installazione  
**Prerequisiti**:
- OpenStack DevStack (già installato e configurato)

1. **Clona il Repository**:
   git clone https://github.com/Ginobuonvino01/openstack-forecasting-plugin.git
   cd openstack-forecasting-plugin
   
2. **Installa le Dipendenze**:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. **Configura l'Ambiente OpenStack**:
   Carica le variabili d'ambiente di DevStack
   source ~/devstack/openrc admin admin

4. **Avvia il Servizio**:

   Metodo 1: Diretto

   python -m forecasting_plugin

   Metodo 2: Via script

   ./demo.sh

# 🎮 Utilizzo
Demo Interattiva:
1. **Avvia il servizio (Terminale 1)**:

   cd ~/progetto

   source venv/bin/activate

   python -m forecasting_plugin

2. **Test API (Terminale 2)**:

   curl http://localhost:5000/api/v1/health | jq

   curl http://localhost:5000/api/v1/metrics/current | jq

   curl "http://localhost:5000/api/v1/forecast/cpu?hours=12" | jq

3. **Controlla OpenStack (Terminale 3)**:

   source ~/devstack/openrc admin admin
   
   openstack server list

# Demo Dinamica con VM:

Sistema vuoto (0 VM attive):

curl http://localhost:5000/api/v1/metrics/current

**Output: {"cpu_percent": 13.8, "ram_percent": 15.9}**

Avvia 2 VM:

openstack server start load-vm-1

openstack server start load-vm-2

Dopo 60s, le metriche aumentano:

curl http://localhost:5000/api/v1/metrics/current

**Output: {"cpu_percent": 35.3, "ram_percent": 29.3}**

**+155% CPU, +84% RAM**

Avvia la 3ª VM:

openstack server start load-vm-3

**Output: {"cpu_percent": 53.0, "ram_percent": 37.4}**

**+284% CPU, +135% RAM**

# 📊 Timeline Reale Dimostrata

11:01:21 - Sistema vuoto (0 VM)
  CPU: 11.1% | RAM: 13.5%

11:09:08 - 2 VM attive (load-vm-1, load-vm-2)
  CPU: 34.0% (+206%) | RAM: 27.9% (+107%)

12:44:11 - 3 VM attive (+ load-vm-3)
  CPU: 53.0% (+384%) | RAM: 37.4% (+177%)


📁 Struttura del Codice

forecasting_plugin/

├── __init__.py              # Inizializzazione modulo

├── __main__.py              # Punto d'ingresso

├── api.py                   # API Flask (5 endpoint)

├── collector.py             # Intelligente: rileva VM ACTIVE/SHUTOFF

├── config.py                # Configurazioni e soglie

└── predictor.py             # Regressione lineare per forecasting

devstack/                    # Integrazione DevStack

├── plugin.sh               # Script di installazione

└── settings                # Configurazione servizio

README.md                   # Questa documentazione

requirements.txt            # Dipendenze Python

setup.py                    # Pacchetto Python

demo.sh                     # Script demo (opzionale)

# Calcolo metriche realistiche basate su VM attive

def calculate_realistic_usage(self, server_info):

    # BASE: Utilizzo minimo sistema (5% CPU, 10% RAM)
    
    # PER VM: +12% CPU, +8% RAM per VM attiva
    
    # RISORSE: Calcolo da flavor (vCPUs, RAM)
    
    # GIORNALIERO: Pattern realistico (picco 14:00)
    
    # RANDOM: Variabilità naturale


Predictor ML (predictor.py):

# Regressione lineare semplice ma efficace

def simple_linear_regression(self, data_points, forecast_hours):

    # y = mx + b
    
    # Calcolo trend basato su ultime 168 ore (7 giorni)
    
    # Clip valori tra 0-100% per metriche realistiche


API REST (api.py):

@app.route('/api/v1/health', methods=['GET'])

def health_check():

    """Stato servizio, metriche live, versione"""
    
    return jsonify({
    
        'status': 'healthy',
        
        'metrics': current_metrics,
        
        'openstack_connected': collector.conn is not None
    })
    

# 📈 Risultati e Metriche

Timeline Demo Reale:

11:01:21 - Sistema vuoto (0 VM)

  CPU: 11.1% | RAM: 13.5%

11:09:08 - 2 VM attive
  
  CPU: 34.0% (+206%) | RAM: 27.9% (+107%)

12:44:11 - 3 VM attive  
  
  CPU: 53.0% (+384%) | RAM: 37.4% (+177%)
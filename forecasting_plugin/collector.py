# forecasting_plugin/collector.py
import os
import time
import threading
from datetime import datetime
from openstack import connection


class OpenStackMetricsCollector:
    """Raccoglie metriche reali da OpenStack Nova e Cinder"""

    def __init__(self, interval=300):
        """
        Inizializza il collector con le credenziali OpenStack
        Le credenziali vengono prese da variabili d'ambiente o da config
        """
        self.interval = interval  # secondi tra le raccolte
        self.running = False
        self.metrics_history = {
            'cpu': [],
            'ram': [],
            'storage': []
        }

        # Credenziali OpenStack (devono essere configurate)
        self.auth_url = os.getenv('OS_AUTH_URL', 'http://controller:5000/v3')
        self.username = os.getenv('OS_USERNAME', 'admin')
        self.password = os.getenv('OS_PASSWORD', 'secret')
        self.project_name = os.getenv('OS_PROJECT_NAME', 'admin')

        # Connessione OpenStack
        self.conn = None

    def connect(self):
        """Stabilisce la connessione a OpenStack"""
        try:
            self.conn = connection.Connection(
                auth_url=self.auth_url,
                username=self.username,
                password=self.password,
                project_name=self.project_name,
                user_domain_name="Default",
                project_domain_name="Default"
            )
            print(f"✅ Connesso a OpenStack: {self.auth_url}")
            return True
        except Exception as e:
            print(f"❌ Errore connessione OpenStack: {e}")
            print("Usando dati mock...")
            return False

    def collect_nova_metrics(self):
        """Raccoglie metriche CPU e RAM da Nova"""
        try:
            # Ottieni statistica degli hypervisor
            hypervisors = list(self.conn.compute.hypervisors())

            if not hypervisors:
                print("Nessun hypervisor trovato")
                return None

            # Calcola utilizzo totale CPU
            total_vcpus = sum(h.vcpus for h in hypervisors)
            used_vcpus = sum(h.vcpus_used for h in hypervisors)
            cpu_percent = (used_vcpus / total_vcpus * 100) if total_vcpus > 0 else 0

            # Calcola utilizzo totale RAM
            total_ram = sum(h.memory_size for h in hypervisors)
            used_ram = sum(h.memory_used for h in hypervisors)
            ram_percent = (used_ram / total_ram * 100) if total_ram > 0 else 0

            return {
                'cpu_percent': cpu_percent,
                'ram_percent': ram_percent,
                'hypervisor_count': len(hypervisors),
                'instances': sum(h.running_vms for h in hypervisors)
            }

        except Exception as e:
            print(f"❌ Errore raccolta metriche Nova: {e}")
            return None

    def collect_cinder_metrics(self):
        """Raccoglie metriche storage da Cinder"""
        try:
            # Ottieni tutti i volumi
            volumes = list(self.conn.block_storage.volumes())

            total_size = sum(v.size for v in volumes)
            available_size = sum(v.size for v in volumes if v.status == 'available')
            in_use_size = sum(v.size for v in volumes if v.status == 'in-use')

            return {
                'total_gb': total_size,
                'available_gb': available_size,
                'in_use_gb': in_use_size,
                'volume_count': len(volumes)
            }

        except Exception as e:
            print(f"❌ Errore raccolta metriche Cinder: {e}")
            return None

    def collect_once(self):
        """Raccoglie metriche una volta"""
        if not self.conn:
            if not self.connect():
                return False

        nova_metrics = self.collect_nova_metrics()
        cinder_metrics = self.collect_cinder_metrics()

        if nova_metrics:
            self.metrics_history['cpu'].append({
                'timestamp': datetime.now().isoformat(),
                'value': nova_metrics['cpu_percent']
            })
            self.metrics_history['ram'].append({
                'timestamp': datetime.now().isoformat(),
                'value': nova_metrics['ram_percent']
            })

        if cinder_metrics:
            self.metrics_history['storage'].append({
                'timestamp': datetime.now().isoformat(),
                'value': cinder_metrics['total_gb']
            })

        # Mantieni solo ultime 1000 letture
        for key in self.metrics_history:
            self.metrics_history[key] = self.metrics_history[key][-1000:]

        return True

    def start_collection(self):
        """Avvia la raccolta periodica in background"""
        self.running = True

        def collection_loop():
            while self.running:
                self.collect_once()
                time.sleep(self.interval)

        thread = threading.Thread(target=collection_loop, daemon=True)
        thread.start()
        print(f"✅ Raccolta metriche avviata (intervallo: {self.interval}s)")

    def stop_collection(self):
        """Ferma la raccolta periodica"""
        self.running = False

    def get_metrics_history(self):
        """Restituisce lo storico delle metriche"""
        return self.metrics_history

    def get_current_metrics(self):
        """Restituisce le metriche più recenti"""
        current = {}
        for key in self.metrics_history:
            if self.metrics_history[key]:
                current[key] = self.metrics_history[key][-1]
            else:
                current[key] = {'timestamp': datetime.now().isoformat(), 'value': 0}
        return current


# Collector globale
collector = OpenStackMetricsCollector(interval=300)  # 5 minuti
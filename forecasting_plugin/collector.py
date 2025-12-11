import os
import time
import threading
from datetime import datetime
from openstack import connection


class OpenStackMetricsCollector:
    """Raccoglie metriche reali da OpenStack Nova e Cinder"""

    def __init__(self, interval=300):
        self.interval = interval  # secondi tra le raccolte
        self.running = False
        self.conn = None
        self.metrics_history = {
            'cpu': [],
            'ram': [],
            'storage': []
        }

        # Credenziali OpenStack
        self.auth_url = os.getenv('OS_AUTH_URL', 'http://controller:5000/v3')
        self.username = os.getenv('OS_USERNAME', 'admin')
        self.password = os.getenv('OS_PASSWORD', 'secret')
        self.project_name = os.getenv('OS_PROJECT_NAME', 'admin')

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
            print("⚠️  Userò dati mock per la demo")
            return False

    def collect_real_metrics(self):
        """Raccoglie metriche reali da OpenStack"""
        if not self.conn:
            if not self.connect():
                return False

        try:
            # Metriche da Nova (CPU/RAM)
            hypervisors = list(self.conn.compute.hypervisors())
            if hypervisors:
                total_vcpus = sum(h.vcpus for h in hypervisors)
                used_vcpus = sum(h.vcpus_used for h in hypervisors)
                cpu_percent = (used_vcpus / total_vcpus * 100) if total_vcpus > 0 else 0

                total_ram = sum(h.memory_size for h in hypervisors)
                used_ram = sum(h.memory_used for h in hypervisors)
                ram_percent = (used_ram / total_ram * 100) if total_ram > 0 else 0
            else:
                cpu_percent = ram_percent = 0

            # Metriche da Cinder (Storage)
            volumes = list(self.conn.block_storage.volumes())
            total_storage = sum(v.size for v in volumes)

            timestamp = datetime.now().isoformat()

            self.metrics_history['cpu'].append({
                'timestamp': timestamp,
                'value': cpu_percent,
                'source': 'openstack'
            })

            self.metrics_history['ram'].append({
                'timestamp': timestamp,
                'value': ram_percent,
                'source': 'openstack'
            })

            self.metrics_history['storage'].append({
                'timestamp': timestamp,
                'value': total_storage,
                'source': 'openstack'
            })

            print(f"📊 Metriche reali: CPU={cpu_percent:.1f}%, RAM={ram_percent:.1f}%, Storage={total_storage}GB")
            return True

        except Exception as e:
            print(f"❌ Errore raccolta metriche reali: {e}")
            return False

    def collect_mock_metrics(self):
        """Genera dati mock quando OpenStack non è disponibile"""
        import random
        import numpy as np

        hour_of_day = datetime.now().hour
        minute = datetime.now().minute

        # Pattern realistico
        time_factor = hour_of_day + minute / 60
        cpu_val = 30 + 20 * np.sin(time_factor * np.pi / 12) + random.uniform(-5, 5)
        ram_val = 40 + 15 * np.sin(time_factor * np.pi / 12) + random.uniform(-3, 3)

        # Storage crescente
        if self.metrics_history['storage']:
            last_storage = self.metrics_history['storage'][-1]['value']
            storage_val = last_storage + random.uniform(0, 0.1)
        else:
            storage_val = 500

        timestamp = datetime.now().isoformat()

        self.metrics_history['cpu'].append({
            'timestamp': timestamp,
            'value': max(10, min(100, cpu_val)),
            'source': 'mock'
        })

        self.metrics_history['ram'].append({
            'timestamp': timestamp,
            'value': max(20, min(100, ram_val)),
            'source': 'mock'
        })

        self.metrics_history['storage'].append({
            'timestamp': timestamp,
            'value': storage_val,
            'source': 'mock'
        })

        print(f"📊 Metriche mock: CPU={cpu_val:.1f}%, RAM={ram_val:.1f}%, Storage={storage_val:.1f}GB")
        return True

    def collect_once(self):
        """Tenta di raccogliere metriche reali, altrimenti usa mock"""
        success = False

        if self.conn:
            success = self.collect_real_metrics()

        if not success:
            success = self.collect_mock_metrics()

        # Mantieni solo ultimi 1000 punti
        for key in self.metrics_history:
            if len(self.metrics_history[key]) > 1000:
                self.metrics_history[key] = self.metrics_history[key][-1000:]

        return success

    def start_collection(self):
        """Avvia la raccolta periodica in background"""
        self.running = True

        def collection_loop():
            while self.running:
                self.collect_once()
                time.sleep(self.interval)

        thread = threading.Thread(target=collection_loop, daemon=True)
        thread.start()
        print(f"✅ Collector avviato (intervallo: {self.interval}s)")

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
                current[key] = {'timestamp': datetime.now().isoformat(), 'value': 0, 'source': 'none'}
        return current

    def get_openstack_info(self):
        """Restituisce informazioni sulla connessione OpenStack"""
        if self.conn:
            try:
                hypervisors = list(self.conn.compute.hypervisors())
                volumes = list(self.conn.block_storage.volumes())

                return {
                    'connected': True,
                    'auth_url': self.auth_url,
                    'hypervisors': len(hypervisors),
                    'volumes': len(volumes)
                }
            except:
                return {'connected': False, 'error': 'Connection lost'}
        else:
            return {'connected': False, 'message': 'Not connected'}


# Istanza globale
collector = OpenStackMetricsCollector(interval=300)  # 5 minuti
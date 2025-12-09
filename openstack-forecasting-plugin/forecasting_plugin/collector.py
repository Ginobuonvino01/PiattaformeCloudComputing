import time
from datetime import datetime, timedelta
from openstack import connection


class MetricsCollector:
    def __init__(self, auth_url, username, password, project_name):
        self.conn = connection.Connection(
            auth_url=auth_url,
            username=username,
            password=password,
            project_name=project_name,
            user_domain_name="Default",
            project_domain_name="Default"
        )

    def collect_nova_metrics(self):
        """Raccoglie metriche CPU e RAM da Nova"""
        metrics = {
            'timestamp': datetime.now(),
            'cpu_usage': [],
            'ram_usage': [],
            'instances': []
        }

        # Esempio: get hypervisor stats
        hypervisors = list(self.conn.compute.hypervisors())
        for hv in hypervisors:
            metrics['cpu_usage'].append({
                'hypervisor': hv.name,
                'used': hv.vcpus_used,
                'total': hv.vcpus,
                'percent': (hv.vcpus_used / hv.vcpus * 100) if hv.vcpus > 0 else 0
            })

            metrics['ram_usage'].append({
                'hypervisor': hv.name,
                'used_mb': hv.memory_used,
                'total_mb': hv.memory_size,
                'percent': (hv.memory_used / hv.memory_size * 100) if hv.memory_size > 0 else 0
            })

        return metrics

    def collect_cinder_metrics(self):
        """Raccoglie metriche storage da Cinder"""
        metrics = {
            'timestamp': datetime.now(),
            'volumes': [],
            'total_usage_gb': 0
        }

        volumes = list(self.conn.block_storage.volumes())
        for vol in volumes:
            metrics['volumes'].append({
                'id': vol.id,
                'size_gb': vol.size,
                'status': vol.status
            })
            metrics['total_usage_gb'] += vol.size

        return metrics
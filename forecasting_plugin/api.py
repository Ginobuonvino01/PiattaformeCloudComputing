# forecasting_plugin/api.py
from flask import Flask, jsonify, request
from datetime import datetime
from .collector import collector
from .config import Config
from .predictor import ResourcePredictor

app = Flask(__name__)

# Avvia il collector
collector.start_collection()


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    metrics = collector.get_current_metrics()
    return jsonify({
        'status': 'healthy',
        'service': 'openstack-forecasting-plugin',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'metrics_collected': {
            'cpu': len(collector.metrics_history['cpu']),
            'ram': len(collector.metrics_history['ram']),
            'storage': len(collector.metrics_history['storage'])
        },
        'openstack_connected': collector.conn is not None,
        'auth_url': collector.auth_url
    })


@app.route('/api/v1/forecast/cpu', methods=['GET'])
def forecast_cpu():
    try:
        hours = request.args.get('hours', default=24, type=int)

        values = [m['value'] for m in collector.metrics_history['cpu'][-168:]]

        if len(values) < 2:
            return jsonify({
                'error': 'Not enough real data for forecasting',
                'data_points': len(values),
                'suggestion': 'Wait for the collector to gather more metrics'
            }), 400

        predictor = ResourcePredictor()
        forecast = predictor.simple_linear_regression(values, forecast_hours=hours)

        return jsonify({
            'metric': 'cpu_usage_percent',
            'historical_count': len(values),
            'forecast_hours': hours,
            'predictions': forecast,
            'current_value': values[-1] if values else 0,
            'trend': 'increasing' if forecast[-1] > forecast[0] else 'decreasing',
            'data_source': 'OpenStack Nova (real)' if collector.conn else 'Mock data',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/openstack/info', methods=['GET'])
def openstack_info():
    """Endpoint per informazioni su OpenStack"""
    if collector.conn:
        try:
            # Ottieni informazioni di base su OpenStack
            hypervisors = list(collector.conn.compute.hypervisors())
            volumes = list(collector.conn.block_storage.volumes())

            return jsonify({
                'connected': True,
                'auth_url': collector.auth_url,
                'hypervisors': len(hypervisors),
                'volumes': len(volumes),
                'instances': sum(h.running_vms for h in hypervisors),
                'total_vcpus': sum(h.vcpus for h in hypervisors),
                'total_ram_gb': sum(h.memory_size for h in hypervisors) / 1024,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'connected': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    else:
        return jsonify({
            'connected': False,
            'message': 'Not connected to OpenStack',
            'timestamp': datetime.now().isoformat()
        })

# Gli altri endpoint rimangono simili ma usano collector.metrics_history
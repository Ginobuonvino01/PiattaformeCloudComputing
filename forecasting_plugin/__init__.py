"""
OpenStack AI Resource Forecasting Plugin
"""

from .collector import collector, OpenStackMetricsCollector
from .predictor import ResourcePredictor
from .config import Config

__version__ = '2.0.0'
__all__ = ['collector', 'OpenStackMetricsCollector', 'ResourcePredictor', 'Config']
# forecasting_plugin/__init__.py
from .collector import collector
from .api import app

__all__ = ['collector', 'app']
__version__ = '2.0.0'
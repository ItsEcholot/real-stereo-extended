"""Main module which starts the real-stereo application."""

from tracking.manager import TrackingManager
from api.manager import ApiManager
from config import Config


config = Config()

tracking = TrackingManager()
# tracking.start_tracking()

api = ApiManager(config, tracking)
api.start_api()

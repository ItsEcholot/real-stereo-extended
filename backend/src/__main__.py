"""Main module which starts the real-stereo application."""

from tracking.manager import TrackingManager
from api.manager import ApiManager


tracking = TrackingManager()
# tracking.start_tracking()

api = ApiManager('master', tracking)
api.start_api()

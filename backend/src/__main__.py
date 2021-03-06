from tracking.manager import TrackingManager
from api.manager import ApiManager


tracking = TrackingManager()
tracking.start_tracking()

api = ApiManager(tracking)
api.start_api()

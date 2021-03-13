"""Main module which starts the real-stereo application."""

from sys import argv
from tracking.manager import TrackingManager
from api.manager import ApiManager
from config import Config, NodeType
from protocol.server import ClusterServer
from protocol.client import ClusterClient


config = Config()

print('Starting as ' + str(config.type))
if config.type == NodeType.MASTER or '--master' in argv:
    cluster_server = ClusterServer()
    cluster_server.start()
else:
    cluster_client = ClusterClient()
    cluster_client.start()

tracking = TrackingManager()
# tracking.start_tracking()

api = ApiManager(config, tracking)
api.start_api()

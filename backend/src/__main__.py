"""Main module which starts the real-stereo application."""

from sys import argv
from tracking.manager import TrackingManager
from api.manager import ApiManager
from config import Config, NodeType
from balancing.manager import BalancingManager
from protocol.master import ClusterMaster
from protocol.slave import ClusterSlave


config = Config()
balancing = BalancingManager(config)

print('Starting as ' + str(config.type))
if config.type == NodeType.MASTER or '--master' in argv:
    cluster_master = ClusterMaster(config)
    cluster_master.start()
    balancing.start_discovery()
else:
    cluster_slave = ClusterSlave()
    cluster_slave.start()

tracking = TrackingManager()
# tracking.start_tracking()

api = ApiManager(config, tracking)
api.start_api()

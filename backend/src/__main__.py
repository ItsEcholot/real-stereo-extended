"""Main module which starts the real-stereo application."""

from sys import argv
import asyncio
from tracking.manager import TrackingManager
from api.manager import ApiManager
from config import Config, NodeType
from balancing.manager import BalancingManager
from protocol.master import ClusterMaster
from protocol.slave import ClusterSlave


async def main():
    """Starts all parts of the application."""
    config = Config()

    print('Starting as ' + str(config.type))

    tracking = TrackingManager(config)

    if config.type == NodeType.MASTER or '--master' in argv:
        cluster_slave = ClusterSlave(config, tracking)
        cluster_master = ClusterMaster(config, cluster_slave)
        balancing = BalancingManager(config)
        api = ApiManager(config, tracking, cluster_master, balancing)

        await asyncio.gather(
            cluster_master.start(),
            api.start(),
            balancing.start_discovery(),
            balancing.start_control(),
        )
    else:
        cluster_slave = ClusterSlave(config, tracking)
        api = ApiManager(config, tracking)

        await asyncio.gather(
            cluster_slave.start(),
            api.start(),
        )


asyncio.run(main())

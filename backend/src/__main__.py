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
    """Starts all part of the application."""
    config = Config()

    print('Starting as ' + str(config.type))

    tracking = TrackingManager()
    api = ApiManager(config, tracking)

    if config.type == NodeType.MASTER or '--master' in argv:
        cluster_master = ClusterMaster(config)
        balancing = BalancingManager(config)

        await asyncio.gather(
            cluster_master.start(),
            # tracking.start(),
            api.start(),
            balancing.start_discovery(),
        )
    else:
        cluster_slave = ClusterSlave()

        await asyncio.gather(
            cluster_slave.start(),
            # tracking.start(),
            api.start(),
        )


asyncio.run(main())

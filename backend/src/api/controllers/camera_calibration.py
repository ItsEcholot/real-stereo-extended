"""Controller for the /camera-calibration namespace."""

from socketio import AsyncNamespace
from config import Config
from models.acknowledgment import Acknowledgment
from api.validate import Validate
from protocol.master import ClusterMaster


class CameraCalibrationController(AsyncNamespace):
    """Controller for the /camera-calibration namespace."""

    def __init__(self, config: Config, cluster_master: ClusterMaster):
        super().__init__(namespace='/camera-calibration')
        self.config: Config = config
        self.cluster_master: ClusterMaster = cluster_master

    def validate(self, data: dict) -> Acknowledgment:  # pylint: disable=no-self-use
        """Validates the input data.

        :param dict data: Input data
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        start = data.get('start')
        finish = data.get('finish')
        repeat = data.get('repeat')

        if start is not None:
            validate.boolean(start, label='Start')
        if finish is not None:
            validate.boolean(finish, label='Finish')
        if repeat is not None:
            validate.boolean(repeat, label='Repeat')
        if data.get('node') is None or isinstance(data.get('node'), dict) is False:
            ack.add_error('Node id must not be empty')
        elif validate.integer(data.get('node').get('id'), label='Node id', min_value=1):
            if self.config.node_repository.get_node(data.get('node').get('id')) is None:
                ack.add_error('A node with this id does not exist')

        return ack

    async def on_update(self, _: str, data: dict) -> None:
        """Updates the camera calibration process.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data)

        # update the camera calibration process
        if ack.successful:
            node = self.config.node_repository.get_node(data.get('node').get('id'))
            start = data.get('start')
            finish = data.get('finish')
            repeat = data.get('repeat')
            self.cluster_master.send_camera_calibration_request(node.ip_address, start=start,
                                                                finish=finish, repeat=repeat)

        return ack.to_json()

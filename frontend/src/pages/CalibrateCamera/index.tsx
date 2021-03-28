import { Alert, Button, Col, Divider, Row, Space } from 'antd';
import { FunctionComponent, useCallback, useState } from 'react';
import { RadarChartOutlined, CheckOutlined, DeleteOutlined } from '@ant-design/icons';
import { useSettings } from '../../services/settings';
import { useNodes } from '../../services/nodes';
import { useCameraCalibration } from '../../services/cameraCalibration';
import { useHistory } from 'react-router';

type CalibrateCameraPageProps = {
  nodeId: number;
}

const CalibrateCameraPage: FunctionComponent<CalibrateCameraPageProps> = ({ nodeId }) => {
  const history = useHistory();
  const { settings } = useSettings();
  const { nodes } = useNodes();
  const currentNode = nodes?.find(node => node.id === nodeId);
  const { cameraCalibration, updateCameraCalibration } = useCameraCalibration(currentNode?.id)
  const [started, setStarted] = useState<boolean>(false);
  const [errors, setErrors] = useState<string[]>();
  const count = cameraCalibration ? cameraCalibration.count : 0;

  const startCalibration = useCallback(async () => {
    setStarted(true);
    try {
      await updateCameraCalibration({ start: true });
    } catch (ack) {
      setErrors(ack.errors);
    }
  }, [updateCameraCalibration]);

  const finishCalibration = useCallback(async () => {
    try {
      await updateCameraCalibration({ finish: true });
      history.push(`/nodes/${nodeId}`)
    } catch (ack) {
      setErrors(ack.errors);
    }
  }, [updateCameraCalibration, history, nodeId]);

  const cancelCalibration = useCallback(async () => {
    try {
      await updateCameraCalibration({ finish: true, repeat: true });
      history.push(`/nodes/${nodeId}`);
    } catch (ack) {
      setErrors(ack.errors);
    }
  }, [updateCameraCalibration, history, nodeId]);

  if (currentNode && started) {
    return (
      <>
        {errors?.map((error, index) => (
          <Alert key={index} message={error} type="error" showIcon />
        ))}
        <Row gutter={[0, 16]}>
          <Col span={24}>{count} images used</Col>
          <Col span={24}>
            <img
              width="100%"
              alt="Camera Preview"
              src={`http://${currentNode.ip}:8080/stream.mjpeg`} />
          </Col>
          <Col span={24}>
            <Space>
              <Button danger icon={<DeleteOutlined />} onClick={cancelCalibration}>Cancel</Button>
            </Space>
          </Col>
        </Row>
      </>
    );
  }

  return (
    <Row>
      <Col>
        <p>
          Each camera node gets shipped with a default calibration.
        </p>
        <p>
          In case it is not sufficient or person detection and tracking does not work reliable, the camera can be calibrated maunally.
        </p>
        <p>
          To do so, download the <a href="/backend-assets/chessboard.pdf" target="_blank" rel="noreferrer">chessboard pdf</a> and print it on a paper.
        </p>
        <p>
          After clicking on "Start calibration", hold the chessboard in front of the camera.
          Make sure the paper is flat during this process.
          It may help to clamp the paper to a clipboard or another hard surface.
        </p>
        <p>
          You have 3 seconds of time before a chessboard will be searched in the camera stream.
          And when the chessboard has been detected, you can review it.
        </p>
        <Divider />
        <p>
          Repeat the process a few times and always hold the chessboard in different angles and rotations.
          An example can be seen <a href="https://upload.wikimedia.org/wikipedia/commons/0/05/Multiple_chessboard_views.png" target="_blank" rel="noreferrer">here</a>.
        </p>
        <p>
          More images improve the calibration.
          For a reliable configuration, at least <b>10 images</b> should be used.
        </p>
        <Divider />
        {!settings || settings.balance
          ? <Button type="text" disabled>Balancing must be disabled</Button>
          : <Button type="primary" icon={<RadarChartOutlined />} onClick={startCalibration}>Start calibration</Button>}
      </Col>
    </Row>
  )
};

export default CalibrateCameraPage;

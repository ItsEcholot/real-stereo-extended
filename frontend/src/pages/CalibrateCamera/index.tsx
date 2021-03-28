import { Button, Col, Divider, Row } from 'antd';
import { FunctionComponent } from 'react';
import { RadarChartOutlined } from '@ant-design/icons';
import { useSettings } from '../../services/settings';

type CalibrateCameraPageProps = {
  nodeId: number;
}

const CalibrateCameraPage: FunctionComponent<CalibrateCameraPageProps> = ({ nodeId }) => {
  const { settings } = useSettings();

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
          To do so, download the <a href="/backend-assets/chessboard.pdf" target="_blank">chessboard pdf</a> and print it on a paper.
        </p>
        <p>
          After clicking on "Start calibration", hold the chessboard in front of the camera.
          Make sure the paper is flat during this process.
          It may help to clip the paper to a clipboard or another hard surface.
        </p>
        <p>
          When the chessboard has been detected, you can review it.
        </p>
        <Divider />
        <p>
          Repeat the process a few times and always hold the chessboard in different angles and rotations.
          An example can be seen <a href="https://upload.wikimedia.org/wikipedia/commons/0/05/Multiple_chessboard_views.png" target="_blank">here</a>.
        </p>
        <p>
          More images improve the calibration.
          For a reliable configuration, at least <b>10 images</b> should be used.
        </p>
        <Divider />
        {!settings || settings.balance
          ? <Button type="text" disabled>Balancing must be disabled</Button>
          : <Button type="primary" icon={<RadarChartOutlined />}>Start calibration</Button>}
      </Col>
    </Row>
  )
};

export default CalibrateCameraPage;

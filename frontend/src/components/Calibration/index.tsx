import { FunctionComponent, useRef, useState } from 'react';
import { Button, Alert, Space } from 'antd';
import {
  RadarChartOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useRoomCalibration } from '../../services/roomCalibration';
import styles from './styles.module.css';

type CalibrationProps = {
  roomId: number;
}

const Calibration: FunctionComponent<CalibrationProps> = ({ roomId }) => {
  const calibrationMapCanvasRef = useRef<HTMLCanvasElement>(null);
  const {
    roomCalibration,
    errors,
    startCalibration,
    finishCalibration,
  } = useRoomCalibration(roomId, calibrationMapCanvasRef);

  const [calibrationStarting, setCalibrationStarting] = useState(false);
  const [calibrationFinishing, setCalibrationFinishing] = useState(false);

  const onStartCalibration = async () => {
    setCalibrationStarting(true);
    await startCalibration();
  }

  const onFinishCalibration = async () => {
    setCalibrationStarting(false);
    setCalibrationFinishing(true);
    await finishCalibration();
    setCalibrationFinishing(false);
  }

  return (
    <>
      {errors.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      {!roomCalibration?.calibrating ?
        <Button type="primary" loading={calibrationStarting} icon={<RadarChartOutlined />} onClick={onStartCalibration}>
          Start calibration
      </Button> :
        <>
          <Space direction="vertical" className={styles.space}>
            <Button type="primary" loading={calibrationFinishing} icon={<CheckOutlined />} onClick={onFinishCalibration}>Finish calibration</Button>
            <div>
              <span>Current calibration map</span>
              <canvas className={styles.canvas} ref={calibrationMapCanvasRef} />
            </div>
          </Space>
        </>
      }
    </>
  );
}

export default Calibration;
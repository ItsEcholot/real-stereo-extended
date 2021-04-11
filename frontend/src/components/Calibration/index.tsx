import { FunctionComponent, useEffect, useState } from 'react';
import { Button, Alert } from 'antd';
import {
  RadarChartOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useRoomCalibration } from '../../services/roomCalibration';

type CalibrationProps = {
  roomId: number;
}

const Calibration: FunctionComponent<CalibrationProps> = ({roomId}) => {
  const { 
    setRoomId,
    roomCalibration,
    errors,
    startCalibration,
    finishCalibration,
  } = useRoomCalibration();

  const [calibrationStarting, setCalibrationStarting] = useState(false);
  const [calibrationFinishing, setCalibrationFinishing] = useState(false);

  useEffect(() => {
    setRoomId(roomId);
    return () => {
      setRoomId(undefined);
    }
  }, [roomId, setRoomId]);

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
      <Button type="primary" loading={calibrationFinishing} icon={<CheckOutlined />} onClick={onFinishCalibration}>Finish calibration</Button>
      </>
    }
    </>
  );
}

export default Calibration;
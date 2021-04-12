import { FunctionComponent, useEffect, useRef, useState } from 'react';
import { Button, Alert, Space, Row, Col, Steps, Divider } from 'antd';
import {
  RadarChartOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useRoomCalibration } from '../../services/roomCalibration';
import styles from './styles.module.css';
import { Speaker } from '../../services/speakers';

type CalibrationProps = {
  roomId: number;
  roomSpeakers: Speaker[];
}

const Calibration: FunctionComponent<CalibrationProps> = ({
  roomId, 
  roomSpeakers,
}) => {
  const calibrationMapCanvasRef = useRef<HTMLCanvasElement>(null);
  const {
    roomCalibration,
    errors,
    startCalibration,
    finishCalibration,
    nextPosition,
    nextSpeaker,
  } = useRoomCalibration(roomId, calibrationMapCanvasRef);

  const [calibrationStarting, setCalibrationStarting] = useState(false);
  const [calibrationFinishing, setCalibrationFinishing] = useState(false);
  const [calibrationNextPositioning, setCalibrationNextPositioning] = useState(false);
  const [calibrationStep, setCalibrationStep] = useState(0);

  useEffect(() => {
    if (!roomCalibration) return;
    if (roomCalibration.positionFreeze) {
      setCalibrationStep(1 + roomCalibration.currentSpeakerIndex);
    }
  }, [setCalibrationStep, roomCalibration?.positionFreeze, roomCalibration?.currentSpeakerIndex]);

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

  const onNextPosition = async () => {
    setCalibrationNextPositioning(true);
    await nextPosition();
    setCalibrationNextPositioning(false);
    await nextSpeaker();
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
            <Space>
              <Button type="primary" loading={calibrationFinishing} icon={<CheckOutlined />} onClick={onFinishCalibration}>Finish calibration</Button>
            </Space>
            <Divider/>
            <Row gutter={10}>
              <Col span="6">
                <canvas className={styles.canvas} ref={calibrationMapCanvasRef} />
              </Col>
              <Col span="18">
                <Steps progressDot direction="vertical" size="small" current={calibrationStep}>
                  <Steps.Step title="Position yourself" description={<>
                    <span>When you're at the desired location press</span>
                    <Button type="default" disabled={calibrationStep !== 0} loading={calibrationNextPositioning} onClick={onNextPosition}>Next Position</Button>
                  </>} />
                  {roomSpeakers.map(speaker => <Steps.Step key={speaker.id} title={`Measuring ${speaker.name}`} />)}
                </Steps>
              </Col>
            </Row>
          </Space>
        </>
      }
    </>
  );
}

export default Calibration;
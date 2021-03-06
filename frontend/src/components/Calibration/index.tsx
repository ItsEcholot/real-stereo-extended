import { FunctionComponent, useEffect, useRef, useState } from 'react';
import { Button, Alert, Space, Row, Col, Steps, Divider, Progress, Slider } from 'antd';
import {
  RadarChartOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useRoomCalibration } from '../../services/roomCalibration';
import styles from './styles.module.css';
import { Speaker, useSpeakers } from '../../services/speakers';

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
    audioMeterErrors,
    prepareCalibration,
    startCalibration,
    finishCalibration,
    nextPoint,
    nextSpeaker,
    confirmPoint,
    repeatPoint,
    volume
  } = useRoomCalibration(roomId, calibrationMapCanvasRef);
  const { speakers } = useSpeakers();

  const [calibrationStarting, setCalibrationStarting] = useState(false);
  const [calibrationVolume, setCalibrationVolume] = useState(0);
  const [calibrationFinishing, setCalibrationFinishing] = useState(false);
  const [calibrationNextPointing, setCalibrationNextPointing] = useState(false);
  const [calibrationConfirmingPoint, setCalibrationConfirmingPoint] = useState(false);
  const [calibrationRepeatingPoint, setCalibrationRepeatingPoint] = useState(false);
  const [calibrationStep, setCalibrationStep] = useState(0);

  useEffect(() => {
    if (!roomCalibration) return;
    if (roomCalibration.positionFreeze) {
      setCalibrationStep(1 + roomCalibration.currentSpeakerIndex);
    } else {
      setCalibrationStep(0);
    }
  }, [setCalibrationStep, roomCalibration]);

  useEffect(() => {
    if (!roomCalibration?.calibrating) return;
    prepareCalibration();
  }, [roomCalibration?.calibrating, prepareCalibration]);

  const onStartCalibration = async () => {
    setCalibrationStarting(true);
    const ack = await startCalibration(calibrationVolume);

    if (!ack.successful) {
      setCalibrationStarting(false);
    }
  }

  const onFinishCalibration = async () => {
    setCalibrationStarting(false);
    setCalibrationFinishing(true);
    await finishCalibration();
    setCalibrationFinishing(false);
  }

  const onNextPoint = async () => {
    if (!speakers) return;
    setCalibrationNextPointing(true);
    await nextPoint();
    setCalibrationNextPointing(false);
    for (const _ of roomSpeakers) {
      await nextSpeaker();
    }
    await nextSpeaker(false); // One more time to stop it
  }

  const onConfirmPosition = async () => {
    setCalibrationConfirmingPoint(true);
    await confirmPoint();
    setCalibrationConfirmingPoint(false);
  }

  const onRepeatPosition = async () => {
    setCalibrationRepeatingPoint(true);
    await repeatPoint();
    onNextPoint();
    setCalibrationRepeatingPoint(false);
  }

  return (
    <>
      {errors.map((error, index) => (
        <Alert key={`e${index}`} message={error} type="error" showIcon />
      ))}
      {audioMeterErrors.map((error, index) => (
        <Alert key={`ame${index}`} message={error} type="error" showIcon />
      ))}
      {!roomCalibration?.calibrating ? <Space direction="vertical" className={styles.space}>
          <Row gutter={10} align="middle">
            <Col>Calibration Volume</Col>
            <Col flex="auto"><Slider defaultValue={30} onChange={setCalibrationVolume} /></Col>
          </Row>
          <Button type="primary" loading={calibrationStarting} icon={<RadarChartOutlined />} onClick={onStartCalibration}>
            {roomCalibration?.previousPoints && roomCalibration.previousPoints.length > 0 ? 'Restart calibration' : 'Start calibration'}
          </Button>
        </Space> :
        <>
          <Space direction="vertical" className={styles.space}>
            <Space>
              <Button type="primary" loading={calibrationFinishing} icon={<CheckOutlined />} onClick={onFinishCalibration}>Finish calibration</Button>
            </Space>
            <Divider />
            <Row gutter={10}>
              <Col span="6">
                <canvas className={styles.canvas} ref={calibrationMapCanvasRef} />
              </Col>
              <Col span="18">
                <Steps progressDot direction="vertical" size="small" current={calibrationStep}>
                  <Steps.Step title="Position yourself" description={<>
                    <span>When you're at the desired location press</span>
                    <br />
                    <Button type="default" disabled={calibrationStep !== 0} loading={calibrationNextPointing} onClick={onNextPoint}>Next Position</Button>
                  </>} />
                  {roomSpeakers.map((speaker, index) => <Steps.Step key={speaker.id} title={`Measuring ${speaker.name}`} description={<>
                    {calibrationStep === index + 1 ?
                      <Progress trailColor="white" percent={Math.round(volume * 100) / 100} /> :
                      roomCalibration.currentPoints[index] ? <Progress trailColor="white" percent={Math.round(roomCalibration.currentPoints[index].measuredVolume * 100) / 100} /> : null}
                  </>} />)}
                  <Steps.Step title="Confirm calibration for this position" description={<>
                    <Space>
                      <Button type="default" disabled={calibrationStep !== roomSpeakers.length + 1} loading={calibrationConfirmingPoint} onClick={onConfirmPosition}>Confirm</Button>
                      <Button type="default" disabled={calibrationStep !== roomSpeakers.length + 1} loading={calibrationRepeatingPoint} onClick={onRepeatPosition}>Repeat</Button>
                    </Space>
                  </>} />
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

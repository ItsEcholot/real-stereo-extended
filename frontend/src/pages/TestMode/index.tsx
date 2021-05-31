import { Row, Col, Switch, Divider, Progress, Space, Alert, Select, Spin, Button } from 'antd';
import { FunctionComponent, useEffect, useRef, useState } from 'react';
import { useAudioMeter } from '../../services/audioMeter';
import { useRooms } from '../../services/rooms';
import { useSpeakers } from '../../services/speakers';
import { useTestMode } from '../../services/testMode';
import styles from './styles.module.css';

const TestModePage: FunctionComponent = () => {
  const { rooms } = useRooms();
  const { speakers } = useSpeakers();
  const [testModeEnabled, setTestModeEnabled] = useState(false);
  const [balancing, setBalancing] = useState(false);
  const [testModeSpeaker, setTestModeSpeaker] = useState<string | null>(null);
  const [testModeRoomId, setTestModeRoomId] = useState<number>();
  const testModeMapCanvasRef = useRef<HTMLCanvasElement>(null);
  const { readyToTestLocation, measurePoint, errors } = useTestMode(testModeEnabled, balancing, testModeSpeaker, testModeMapCanvasRef, testModeRoomId);
  const spectrumAnalyzerCanvasRef = useRef<HTMLCanvasElement>(null);
  const { volume, audioMeterErrors } = useAudioMeter(testModeEnabled, spectrumAnalyzerCanvasRef);

  useEffect(() => {
    if (!rooms) return;
    setTestModeRoomId(rooms[0].id)
  }, [rooms])

  return (
    <>
      {errors.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      {audioMeterErrors.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      <Row>
        <Col flex="auto">Enable test mode</Col>
        <Col>
          <Switch onChange={setTestModeEnabled} />
        </Col>
      </Row>
      <Row className={styles.settingRow}>
        <Col flex="auto">Enable balancing</Col>
        <Col>
          <Switch onChange={setBalancing} />
        </Col>
      </Row>
      <Row className={styles.settingRow}>
        <Col span={12}>Enabled speakers</Col>
        <Col flex="auto">
          <Select
            className={styles.select}
            labelInValue
            onChange={(option: any) => setTestModeSpeaker(option.value)}
            defaultValue={{ label: 'All', value: '' }}
          >
            <Select.Option key="all" value={''}>All</Select.Option>
            {speakers?.map(speaker =>
              <Select.Option key={speaker.id} value={speaker.id}>{speaker.name}</Select.Option>
            )}
          </Select>
        </Col>
      </Row>
      <Divider />
      <Space direction="vertical" style={{ width: '100%' }}>
        <Row>
          <Col span={12}>Current volume</Col>
          <Col flex="auto">
            <Progress trailColor="white" percent={Math.round(volume * 100) / 100} />
          </Col>
        </Row>
        <Row>
          <Col flex="none">Volume Map</Col>
          <Col flex="auto">
            <canvas className={styles.canvas} ref={testModeMapCanvasRef} />
          </Col>
        </Row>
        {rooms ? <Row gutter={10}>
          <Col flex="auto">
            <Select
              className={styles.select}
              labelInValue
              onChange={(option: any) => { setTestModeRoomId(option.value) }}
              defaultValue={{ label: rooms[0].name, value: rooms[0].id }}>
              {rooms.map(room =>
                <Select.Option key={room.id} value={room.id}>{room.name}</Select.Option>
              )}
            </Select>
          </Col>
          <Col>
            <Button type="primary" onClick={measurePoint} disabled={!testModeEnabled} loading={!readyToTestLocation && testModeEnabled}>Measure volume</Button>
          </Col>
        </Row> : <Row justify="center"><Spin /></Row>}
        <Divider />
        <Row>
          <Col flex="none">Spectrum Analyzer</Col>
          <Col flex="auto">
            <canvas className={styles.canvas} ref={spectrumAnalyzerCanvasRef} />
          </Col>
        </Row>
      </Space>
    </>
  );
}

export default TestModePage;

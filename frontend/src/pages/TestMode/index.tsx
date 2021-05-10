import { Row, Col, Switch, Divider, Progress, Space, Alert } from 'antd';
import { FunctionComponent, useRef, useState } from 'react';
import { useAudioMeter } from '../../services/audioMeter';
import { useTestMode } from '../../services/testMode';
import styles from './styles.module.css';

const TestModePage: FunctionComponent = () => {
  const [testModeEnabled, setTestModeEnabled] = useState(false);
  const testModeMapCanvasRef = useRef<HTMLCanvasElement>(null);
  const {readyToTestLocation, errors} = useTestMode(testModeEnabled, testModeMapCanvasRef);
  const spectrumAnalyzerCanvasRef = useRef<HTMLCanvasElement>(null);
  const { volume, audioMeterErrors } = useAudioMeter(testModeEnabled, spectrumAnalyzerCanvasRef);

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
      <Divider />
      <Space direction="vertical" style={{ width: '100%' }}>
        <Row>
          <Col flex="none">Spectrum Analyzer</Col>
          <Col flex="auto">
            <canvas className={styles.canvas} ref={spectrumAnalyzerCanvasRef} />
          </Col>
        </Row>
        <Divider />
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
      </Space>
    </>
  );
}

export default TestModePage;
import { Row, Col, Switch, Divider, Progress, Space, Alert } from 'antd';
import { FunctionComponent, useEffect, useRef, useState } from 'react';
import { useAudioMeter } from '../../services/audioMeter';
import { useSettings } from '../../services/settings';
import { useTestMode } from '../../services/testMode';
import styles from './styles.module.css';

const TestModePage: FunctionComponent = () => {
  const [testModeEnabled, setTestModeEnabled] = useState(false);
  const {readyToTestLocation, errors} = useTestMode(testModeEnabled);
  const spectrumAnalyzerCanvasRef = useRef<HTMLCanvasElement>(null);
  const { volume, audioMeterErrors } = useAudioMeter(testModeEnabled, spectrumAnalyzerCanvasRef);
  const { updateSettings } = useSettings();

  useEffect(() => {
    return () => {
      updateSettings({testMode: false});
    }
  }, []);

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
          <Col span={12}>Current volume</Col>
          <Col flex="auto">
            <Progress trailColor="white" percent={Math.round(volume * 100) / 100} />
          </Col>
        </Row>
        <Row>
          <Col span={24}>Spectrum Analyzer</Col>
        </Row>
        <Row>
          <Col span={24}>
            <canvas className={styles.canvas} width="500" height="255" ref={spectrumAnalyzerCanvasRef} />
          </Col>
        </Row>
        
      </Space>
    </>
  );
}

export default TestModePage;
import { Row, Col, Switch, Divider, Spin } from 'antd';
import { FunctionComponent, useState } from 'react';
import { useSettings } from '../../services/settings';

const TestModePage: FunctionComponent = () => {
  const { settings, updateSettings } = useSettings();

  const [previousSettingsBalancing, setPreviousSettingsBalancing] = useState<boolean>();
  const [testModeEnabled, setTestModeEnabled] = useState(false);

  const onChangeEnableTestMode = (checked: boolean) => {
    if (checked) {
      setPreviousSettingsBalancing(settings?.balance);
      updateSettings({ balance: false });
    } else if (previousSettingsBalancing !== undefined) {
      updateSettings({ balance: previousSettingsBalancing });
      setPreviousSettingsBalancing(undefined);
    }

    setTestModeEnabled(checked);
  }

  return (
    <>
      {settings ? <Row>
        <Col flex="auto">Enable test mode</Col>
        <Col>
          <Switch onChange={onChangeEnableTestMode} />
        </Col>
      </Row> : <Row justify="center"><Spin /></Row>}
      <Divider />
    </>
  );
}

export default TestModePage;
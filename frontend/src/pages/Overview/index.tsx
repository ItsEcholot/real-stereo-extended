import { Col, Divider, Row, Switch, Spin, Alert, Progress, Typography } from 'antd';
import { FunctionComponent, useState } from 'react';
import { useSettings } from '../../services/settings';
import { useBalances } from '../../services/balances';

const { Title } = Typography;

const OverviewPage: FunctionComponent<{}> = () => {
  const { settings, updateSettings } = useSettings();
  const { balances } = useBalances();
  const [saving, setSaving] = useState(false);
  const [saveErrors, setSaveErrors] = useState<string[]>();

  const onChangeEnableBalancing = async (checked: boolean) => {
    setSaving(true);
    try {
      await updateSettings({ balance: checked });
      setSaveErrors(undefined);
    } catch (ack) {
      setSaveErrors(ack.errors);
    }
    setSaving(false);
  };

  return (
    <>
      {saveErrors?.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      {settings ? <Row>
        <Col flex="auto">Enable balancing</Col>
        <Col>
          <Switch defaultChecked={settings?.balance} onChange={onChangeEnableBalancing} loading={saving} />
        </Col>
      </Row> : <Row justify="center"><Spin /></Row>}
      <Divider />
      Current balance:
      {balances?.map(balance => (
        <Row>
          <Col>{balance.speaker.name}</Col>
          <Col>
            <Progress percent={balance.volume} showInfo={false} />
          </Col>
        </Row>
      ))}
    </>
  );
}

export default OverviewPage;
import { Col, Divider, Row, Switch, Spin, Alert, Progress, Typography } from 'antd';
import { FunctionComponent, useState } from 'react';
import { useSettings } from '../../services/settings';
import { Balance, useBalances } from '../../services/balances';
import styles from './styles.module.css';

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

  const roomBalances: Record<string, Balance[]> = {};
  if (balances) {
    balances.forEach((balance) => {
      if (!Object.keys(roomBalances).includes(balance.speaker.room.name)) {
        roomBalances[balance.speaker.room.name] = [];
      }
      roomBalances[balance.speaker.room.name].push(balance);
    });
  }

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
      {balances && balances.length > 0 && settings?.balance && (
        <>
          <Divider />
          <Typography.Title level={4}>Current balance</Typography.Title>
          {Object.keys(roomBalances).map((roomName) => (
            <>
              <Row key={roomName} className={styles.BalanceRoom}>
                <Col><Typography.Text type="secondary">{roomName}</Typography.Text></Col>
              </Row>
              {roomBalances[roomName].map(balance => (
                <Row key={balance.speaker.id}>
                  <Col span={8}>{balance.speaker.name}</Col>
                  <Col span={16}>
                    <Progress trailColor="white" percent={balance.volume} />
                  </Col>
                </Row>
              ))}
            </>
          ))}
        </>
      )}
    </>
  );
}

export default OverviewPage;

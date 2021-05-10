import { FunctionComponent, useState } from 'react';
import { Alert, Button, Col, Form, Input, Row, Spin, Typography } from 'antd';
import { VideoCameraTwoTone, ControlTwoTone, CheckOutlined } from '@ant-design/icons';
import NodeSetupType from '../../components/NodeSetupType';
import { useSettings } from '../../services/settings';
import styles from './styles.module.css';
import { useNetworks } from '../../services/networks';
import { useHistory } from 'react-router';

const SetupPage: FunctionComponent<{}> = () => {
  const history = useHistory();
  const { settings, updateSettings } = useSettings();
  const { createNetwork } = useNetworks();
  const [nodeType, setNodeType] = useState<'master' | 'tracking'>();
  const [saving, setSaving] = useState<boolean>(false);
  const [form] = Form.useForm();
  const [errors, setErrors] = useState<string[]>();

  const save = async (values: { ssid: string, psk: string }) => {
    setSaving(true);

    try {
      if (settings && settings.configured) {
        await createNetwork(values);
      } else {
        await updateSettings({
          balance: false,
          nodeType,
          network: values,
        });
      }

      history.push(`/setup/finished/${nodeType || 'tracking'}`);
    } catch (ack) {
      setSaving(false);
      setErrors(ack.errors);
    }
  };

  if (!settings) {
    return (
      <Row justify="center"><Spin /></Row>
    );
  }

  // require the user to select a node type if it is currently unconfigured
  if (!settings.configured && !nodeType) {
    return (
      <>
        {errors?.map((error, index) => (
          <Alert key={index} message={error} type="error" showIcon />
        ))}
        <Row>
          <Col>
            <Typography.Title level={3}>Welcome to Real Stereo!</Typography.Title>
          </Col>
        </Row>
        <Row>
          <Col>
            <Typography.Text>Is this the first Real Stereo device you are setting up in this network?</Typography.Text>
          </Col>
        </Row>
        <Row>
          <Col>
            <NodeSetupType
              text="Yes, set it up as the coordinator node."
              icon={<ControlTwoTone />}
              onClick={() => setNodeType('master')}
            />
            <NodeSetupType
              text="No, set it up as a camera node and join an existing network."
              icon={<VideoCameraTwoTone />}
              onClick={() => setNodeType('tracking')}
            />
          </Col>
        </Row>
      </>
    );
  }

  // as the second setup, ask for a wireless network to join
  return (
    <>
      {errors?.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      <Row>
        <Typography.Title level={3}>WLAN Configuration</Typography.Title>
        <Typography.Text>
          Each Real Stereo device needs to join the same wireless network in order to communicate with each other.
          Please specify the credentials to join one.
          If you already have other Real Stereo devices running, make sure to use the same network.
        </Typography.Text>
      </Row>
      <Row className={styles.FormRow}>
        <Col xs={24}>
          <Form
            form={form}
            labelCol={{ span: 12 }}
            wrapperCol={{ span: 12 }}
            labelAlign="left"
            onFinish={save}>
            <Form.Item
              label="SSID (Name)"
              name="ssid"
              required
              requiredMark
              rules={[{ required: true, message: 'Please specify a SSID' }]}>
              <Input />
            </Form.Item>
            <Form.Item
              label="Password"
              name="psk"
              rules={[{
                min: 8,
                message: 'Password must be between 8 and 63 characters',
              }, {
                max: 63,
                message: 'Password must be between 8 and 63 characters',
              }]}>
              <Input type="password" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" icon={<CheckOutlined />} htmlType="submit" loading={saving}>Save</Button>
            </Form.Item>
          </Form>
        </Col>
      </Row>
    </>
  );
};

export default SetupPage;

import { FunctionComponent } from 'react';
import { Col, Row, Typography } from 'antd';
import { VideoCameraTwoTone, ControlTwoTone } from '@ant-design/icons';
import styles from './styles.module.css';

type SetupFinishedPageProps = {
  nodeType: 'master' | 'tracking';
}

const SetupFinishedPage: FunctionComponent<SetupFinishedPageProps> = ({ nodeType }) => (
  <>
    <Row justify="center">
      <Col>
        {nodeType === 'master'
          ? <ControlTwoTone className={styles.Icon} />
          : <VideoCameraTwoTone className={styles.Icon} />}
      </Col>
    </Row>
    <Row>
      <Col>
        <Typography.Title level={3}>Setup finished</Typography.Title>
        <Typography.Text>Congratulations, you have just set up a Real Stereo device!</Typography.Text>
        <br />
        <Typography.Text>
          The device will now join the wireless network you have specified.
          If there should be any problem during this process, this configuration WLAN will be available again after one minute and you can modify the configuration.
        </Typography.Text>
        <br />
        {nodeType === 'master'
          ? <Typography.Text>When the device successfully joined the wireless network, the administrator interface is available at https://IP_OF_THE_DEVICE:8080</Typography.Text>
          : <Typography.Text>When the device successfully joined the wireless network, it will automatically connect to the coordinator node and should appear in the administrator interface after about one minute.</Typography.Text>}
      </Col>
    </Row>
  </>
);

export default SetupFinishedPage;

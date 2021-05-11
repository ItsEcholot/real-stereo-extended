import { Card, Col, Row, Typography } from 'antd';
import { FunctionComponent, ReactNode } from 'react';
import styles from './styles.module.css';

type NodeSetupTypeProps = {
  icon: ReactNode;
  text: string;
  onClick: () => void;
}

const NodeSetupType: FunctionComponent<NodeSetupTypeProps> = ({ icon, text, onClick }) => (
  <Card hoverable className={styles.Card} onClick={onClick}>
    <Row justify="center" className={styles.IconRow}>
      <Col>
        {icon}
      </Col>
    </Row>
    <Row justify="center">
      <Col>
        <Typography.Text className={styles.Text}>{text}</Typography.Text>
      </Col>
    </Row>
  </Card>
);

export default NodeSetupType;

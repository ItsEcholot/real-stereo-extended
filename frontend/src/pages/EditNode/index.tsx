import { Row, Col, Divider, Form, Input, Spin, Space, Select, Button, Alert, Badge, Dropdown, Menu, Collapse } from 'antd';
import { FunctionComponent, useState } from 'react';
import {
  CheckOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { useHistory } from 'react-router-dom';
import inactiveImage from '../../assets/camera-inactive.jpg';
import { useNodes } from '../../services/nodes';
import { useRooms } from '../../services/rooms';
import styles from './styles.module.css';

const { Option } = Select;

type EditNodePageProps = {
  nodeId: number;
}

const EditNodePage: FunctionComponent<EditNodePageProps> = ({
  nodeId,
}) => {
  const { nodes, updateNode, deleteNode } = useNodes();
  const { rooms } = useRooms();
  const currentNode = nodes?.find(node => node.id === nodeId);
  const history = useHistory();

  const [saving, setSaving] = useState(false);
  const [saveErrors, setSaveErrors] = useState<string[]>();
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);

  const save = async (values: { name: string, room: number, detector: string }) => {
    if (!currentNode) return;
    setSaving(true);
    try {
      await updateNode({
        ...currentNode,
        name: values.name,
        detector: values.detector,
        room: { id: values.room },
      });
      setSaveErrors(undefined);
      setShowSaveSuccess(true);
      setTimeout(() => setShowSaveSuccess(false), 3000);
    } catch (ack) {
      setSaveErrors(ack.errors);
    }
    setSaving(false);
  }

  const deleteCameraNode = async () => {
    if (!currentNode) return;
    await deleteNode(currentNode.id);
    history.push('/nodes/add');
  }

  return (
    <>
      {currentNode?.ip && (
        <Row>
          <Col>
            <img
              width="100%"
              alt="Camera Preview"
              src={currentNode?.online ? `http://${currentNode?.ip}:8080/stream.mjpeg` : inactiveImage} />
            <Dropdown.Button overlay={(
              <Menu>
                <Menu.Item onClick={() => history.push(`/nodes/${currentNode.id}/calibrate-camera`)}>
                  Calibrate Camera
                </Menu.Item>
              </Menu>
            )} className={styles.CameraOptionsDropdown} />
          </Col>
        </Row>
      )}
      <Row>
        <Col flex="auto">IP Address</Col>
        <Col>{currentNode?.ip}</Col>
      </Row>
      <Row>
        <Col flex="auto">Hostname</Col>
        <Col>{currentNode?.hostname}</Col>
      </Row>
      <Row>
        <Col flex="auto">Status</Col>
        <Col>
          {currentNode?.online
            ? <Badge status="success" text="Online" />
            : <Badge status="error" text="Offline" />
          }</Col>
      </Row>
      <Divider />
      {saveErrors?.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      {showSaveSuccess ? <Alert message="Saved successfully" type="success" showIcon /> : null}
      {currentNode && rooms ? <Form
        labelCol={{ span: 12 }}
        wrapperCol={{ span: 12 }}
        labelAlign="left"
        onFinish={save}
        initialValues={{
          ...currentNode,
          room: currentNode.room?.id,
        }}>
        <Form.Item
          label="Node name"
          name="name"
          rules={[{ required: true, message: 'Please input a name' }]}>
          <Input />
        </Form.Item>
        <Form.Item
          label="Room"
          name="room"
          rules={[{ required: true, message: 'Please select a room' }]}>
          <Select
            placeholder="Select a room">
            {rooms.map(room => <Option key={room.id} value={room.id}>{room.name}</Option>)}
          </Select>
        </Form.Item>
        <Collapse ghost className={styles.AdvancedOptions}>
          <Collapse.Panel header="Advanced Options" key="advanced">
            <Form.Item
              label="Detection Algorithm"
              name="detector">
              <Select defaultValue={currentNode.detector || 'yolo'}>
                <Option value="hog">Histogram of oriented gradients</Option>
                <Option value="yolo">YOLO3 Object Detector</Option>
              </Select>
            </Form.Item>
          </Collapse.Panel>
        </Collapse>
        <Form.Item>
          <Space>
            <Button type="primary" icon={<CheckOutlined />} htmlType="submit" loading={saving}>Save</Button>
            <Button danger icon={<DeleteOutlined />} disabled={!currentNode.room} onClick={deleteCameraNode} loading={saving}>Delete Camera Node</Button>
          </Space>
        </Form.Item>
      </Form> : <Row justify="center"><Spin /></Row>}
    </>
  );
}

export default EditNodePage;

import { FunctionComponent, useState } from 'react';
import { Checkbox, Col, Divider, Form, Input, Row, Button, Space, Alert, Spin } from 'antd';
import {
  RadarChartOutlined,
  CloseOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useHistory } from 'react-router-dom';
import { useRooms } from '../../services/rooms';
import { Acknowledgment } from '../../services/acknowledgment';

type EditRoomPageProps = {
  roomId?: number;
}

const EditRoomPage: FunctionComponent<EditRoomPageProps> = ({
  roomId
}) => {
  const history = useHistory();
  const { rooms, createRoom, updateRoom } = useRooms();
  const currentRoom = rooms?.find(room => room.id === roomId);

  const [saving, setSaving] = useState(false);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const [saveErrors, setSaveErrors] = useState<string[]>();

  const save = (values: { name: string, nodes: string[] }) => {
    setSaving(true);
    if (currentRoom) {
      updateRoom({ id: currentRoom.id, name: values.name }).then(() => {
        setSaving(false);
        setSaveErrors(undefined);
        setShowSaveSuccess(true);
        setTimeout(() => setShowSaveSuccess(false), 3000);
      }).catch((ack: Acknowledgment) => {
        setSaving(false);
        setSaveErrors(ack.errors);
      })
    } else {
      createRoom({ name: values.name }).then(ack => {
        setSaving(false);
        setSaveErrors(undefined);
        history.push(`/rooms/${ack.createdId}/edit`);
        setShowSaveSuccess(true);
        setTimeout(() => setShowSaveSuccess(false), 3000);
      }).catch((ack: Acknowledgment) => {
        setSaving(false);
        setSaveErrors(ack.errors)
      });
    }
  }

  const startCalibration = () => {

  }

  return (
    <Row justify="center">
      <Col xl={8} lg={12} md={16} xs={24}>
        {saveErrors?.map((error, index) => (
          <Alert key={index} message={error} type="error" showIcon />
        ))}
        {showSaveSuccess ? <Alert message="Saved successfully" type="success" showIcon /> : null}
        {(roomId && currentRoom) || (!roomId) ? <Form
          labelCol={{ span: 12 }}
          wrapperCol={{ span: 12 }}
          labelAlign="left"
          onFinish={save}
          initialValues={{
            ...currentRoom,
            nodes: currentRoom?.nodes.map(node => node.id),
          }}>
          <Form.Item
            label="Room name"
            name="name"
            rules={[{ required: true, message: 'Please input a name' }]}>
            <Input />
          </Form.Item>
          <Form.Item
            label="Assigned Sonos players"
            name="nodes">
            <Checkbox.Group
              options={[{ label: 'Sonos 1', value: 1 }, { label: 'Sonos 2', value: 2 }]} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="default" icon={<CloseOutlined />} onClick={() => history.push('/rooms/edit')} disabled={saving}>Cancel</Button>
              <Button type="primary" icon={<CheckOutlined />} htmlType="submit" loading={saving}>Save</Button>
            </Space>
          </Form.Item>
        </Form> : <Row justify="center"><Spin /></Row>}
        <Divider />
        <p>
          Place the two cameras in a ~90° angle to each other.
          <br />
          Make sure that it is as quiet as possible inside the room.
          <br />
          After starting the calibration, move yourself with the microphone to the specified position.
          <br />
          Stand still until you are told to move to the next position.
          <br />
          When the four corner positions are set up, you can add as many additional positions between those corner positions as you like.
          <br />
          When all positions are calibrated, exit the configuration by pressing the save button.
        </p>
        <Button type="primary" icon={<RadarChartOutlined />} onClick={startCalibration}>Start calibration</Button>
      </Col>
    </Row>
  );
}

export default EditRoomPage;
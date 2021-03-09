import { FunctionComponent } from 'react';
import { Checkbox, Col, Divider, Form, Input, Row, Button, Space } from 'antd';
import {
  RadarChartOutlined,
  CloseOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useRooms } from '../../services/rooms';

type EditRoomPageProps = {
  roomId?: number;
}

const EditRoomPage: FunctionComponent<EditRoomPageProps> = () => {
  const { rooms, createRoom, updateRoom } = useRooms();

  return (
    <Row justify="center">
      <Col xl={8} lg={12} md={16} xs={24}>
        <Form
          labelCol={{ span: 12 }}
          wrapperCol={{ span: 12 }}
          labelAlign="left">
          <Form.Item
            label="Room name"
            name="name"
            rules={[{ required: true, message: 'Please input a name' }]}>
            <Input />
          </Form.Item>
          <Form.Item
            label="Assigned Sonos players">
            <Checkbox.Group
              options={['Sonos 1', 'Sonos 2']} />
          </Form.Item>
        </Form>
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
        <Button type="primary" icon={<RadarChartOutlined />}>Start calibration</Button>
        <Divider />
        <Space>
          <Button type="default" icon={<CloseOutlined />}>Cancel</Button>
          <Button type="primary" icon={<CheckOutlined />}>Save</Button>
        </Space>
      </Col>
    </Row>
  );
}

export default EditRoomPage;
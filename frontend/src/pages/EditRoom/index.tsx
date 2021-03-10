import { FunctionComponent } from 'react';
import { Checkbox, Col, Divider, Form, Input, Row, Button, Space } from 'antd';
import {
  RadarChartOutlined,
  CloseOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useHistory } from 'react-router-dom';
import { useRooms } from '../../services/rooms';

type EditRoomPageProps = {
  roomId?: number;
}

const EditRoomPage: FunctionComponent<EditRoomPageProps> = ({
  roomId
}) => {
  const history = useHistory();
  const { rooms, createRoom, updateRoom } = useRooms();
  const currentRoom = rooms?.find(room => room.id === roomId);

  const save = (values: { name: string, nodes: string[] }) => {
    console.dir(values);
  }

  const startCalibration = () => {

  }

  return (
    <Row justify="center">
      <Col xl={8} lg={12} md={16} xs={24}>
        <Form
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
              <Button type="default" icon={<CloseOutlined />} onClick={() => history.push('/rooms/edit')}>Cancel</Button>
              <Button type="primary" icon={<CheckOutlined />} htmlType="submit">Save</Button>
            </Space>
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
        <Button type="primary" icon={<RadarChartOutlined />} onClick={startCalibration}>Start calibration</Button>
      </Col>
    </Row>
  );
}

export default EditRoomPage;
import { FunctionComponent, useState } from 'react';
import { Checkbox, Divider, Form, Input, Row, Button, Space, Alert, Spin } from 'antd';
import {
  RadarChartOutlined,
  CloseOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useHistory } from 'react-router-dom';
import { useRooms } from '../../services/rooms';
import { Acknowledgment } from '../../services/acknowledgment';
import Text from 'antd/lib/typography/Text';
import { useSpeakers } from '../../services/speakers';

type EditRoomPageProps = {
  roomId?: number;
}

const EditRoomPage: FunctionComponent<EditRoomPageProps> = ({
  roomId
}) => {
  const history = useHistory();
  const { rooms, createRoom, updateRoom } = useRooms();
  const { speakers, updateSpeaker, deleteSpeaker } = useSpeakers();
  const currentRoom = rooms?.find(room => room.id === roomId);
  const currentRoomSpeakers = speakers?.filter(speaker => speaker.room.id === currentRoom?.id);

  const [saving, setSaving] = useState(false);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const [saveErrors, setSaveErrors] = useState<string[]>();

  const save = async (values: { name: string, speakers: number[] }) => {
    setSaving(true);
    let ack;
    try {
      if (currentRoom) {
        ack = await updateRoom({ id: currentRoom.id, name: values.name })
      } else {
        ack = await createRoom({ name: values.name });
      }
      const currentRoomId = currentRoom ? currentRoom.id : ack.createdId;

      if (speakers && currentRoomId) {
        await Promise.all(speakers.map(speaker => {
          if (speaker.room.id !== currentRoomId && values.speakers.includes(speaker.id)) {
            return updateSpeaker({ ...speaker, room: { id: currentRoomId } });
          } else if (speaker.room.id === currentRoomId) {
            return deleteSpeaker(speaker.id);
          }
          return undefined;
        }));
      }

      afterSave(ack, !currentRoom);
    } catch (ack) {
      afterFailedSave(ack);
    }
  }

  const afterSave = (ack: Acknowledgment, redirect: boolean = false) => {
    setSaving(false);
    setSaveErrors(undefined);
    setShowSaveSuccess(true);
    setTimeout(() => setShowSaveSuccess(false), 3000);
    if (redirect) history.push(`/rooms/${ack.createdId}/edit`);
  }

  const afterFailedSave = (ack: Acknowledgment) => {
    setSaving(false);
    setSaveErrors(ack.errors);
  }

  const startCalibration = () => {

  }

  return (
    <>
      {saveErrors?.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      {showSaveSuccess ? <Alert message="Saved successfully" type="success" showIcon /> : null}
      {((roomId && currentRoom) || (!roomId)) && speakers !== undefined ? <Form
        labelCol={{ span: 12 }}
        wrapperCol={{ span: 12 }}
        labelAlign="left"
        onFinish={save}
        initialValues={{
          ...currentRoom,
          speakers: currentRoomSpeakers?.map(speaker => speaker.id),
        }}>
        <Form.Item
          label="Room name"
          name="name"
          rules={[{ required: true, message: 'Please input a name' }]}>
          <Input />
        </Form.Item>
        <Form.Item
          label="Assigned Sonos players"
          name="speakers">
          {speakers.length > 0 ? <Checkbox.Group
            options={speakers?.map(speaker => ({ label: speaker.name, value: speaker.id, /*disabled: speaker.room && speaker.room.id !== currentRoom?.id*/ }))} /> : <Text disabled>No speakers</Text>}
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
    </>
  );
}

export default EditRoomPage;
import { FunctionComponent, useEffect, useState } from 'react';
import { Checkbox, Divider, Form, Input, Row, Button, Space, Alert, Spin, Collapse, Select, Typography } from 'antd';
import {
  CloseOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import { useHistory } from 'react-router-dom';
import { useRooms } from '../../services/rooms';
import { Acknowledgment } from '../../services/acknowledgment';
import Text from 'antd/lib/typography/Text';
import { useSpeakers } from '../../services/speakers';
import Calibration from '../../components/Calibration';
import styles from './styles.module.css';

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
  const currentRoomSpeakers = speakers?.filter(speaker => speaker.room?.id === currentRoom?.id);
  const [form] = Form.useForm();

  const [saving, setSaving] = useState(false);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const [saveErrors, setSaveErrors] = useState<string[]>();

  useEffect(() => {
    form.setFieldsValue({
      ...currentRoom,
      speakers: currentRoomSpeakers?.map(speaker => speaker.id),
    });
  }, [form, currentRoom, currentRoomSpeakers]);

  const save = async (values: { name: string, speakers: string[], people_group: string }) => {
    setSaving(true);
    let ack;
    try {
      if (currentRoom) {
        ack = await updateRoom({
          id: currentRoom.id,
          name: values.name,
          people_group: values.people_group,
        })
      } else {
        ack = await createRoom({ name: values.name, people_group: values.people_group });
      }
      const currentRoomId = currentRoom ? currentRoom.id : ack.createdId;

      if (speakers && currentRoomId) {
        await Promise.all(speakers.map(speaker => {
          if (values.speakers.includes(speaker.id)) {
            if (!speaker.room || speaker.room.id !== currentRoomId) {
              return updateSpeaker({ ...speaker, room: { id: currentRoomId } });
            }
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

  return (
    <>
      {saveErrors?.map((error, index) => (
        <Alert key={index} message={error} type="error" showIcon />
      ))}
      {showSaveSuccess ? <Alert message="Saved successfully" type="success" showIcon /> : null}
      {((roomId && currentRoom) || (!roomId)) && speakers !== undefined ? <Form
        form={form}
        labelCol={{ span: 12 }}
        wrapperCol={{ span: 12 }}
        labelAlign="left"
        onFinish={save}>
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
            options={speakers?.map(speaker => ({ label: speaker.name, value: speaker.id, disabled: speaker.room && speaker.room.id !== currentRoom?.id }))} /> : <Text disabled>No speakers</Text>}
        </Form.Item>
        <Collapse ghost className={styles.AdvancedOptions}>
          <Collapse.Panel header="Advanced options" key="advanced">
            <Form.Item
              label="Handle multiple people"
              name="people_group">
              <Select defaultValue="average">
                <Select.Option value="average">Average</Select.Option>
                <Select.Option value="track">Track</Select.Option>
              </Select>
            </Form.Item>
          </Collapse.Panel>
        </Collapse>
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
          You can add as many calibration positions as you want.
          <br />
          After selecting a position by clicking on "Next Position" stand still until all the measurements are done.
          <br />
          After that you can confirm or repeat the last position.
          <br />
          When all positions are calibrated, exit the configuration by pressing "Finish calibration".
        </p>
      {roomId && currentRoomSpeakers?.length ? 
        <Calibration roomId={roomId} roomSpeakers={currentRoomSpeakers}/> :
        <Typography.Text type="warning">Room needs to be saved & have speakers assigned before calibration can be started</Typography.Text>
      }
    </>
  );
}

export default EditRoomPage;

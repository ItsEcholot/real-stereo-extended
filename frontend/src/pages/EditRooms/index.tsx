import { Button, List, Space, Alert } from 'antd';
import { FunctionComponent, useState } from 'react';
import { useRooms } from '../../services/rooms';
import {
  PlusOutlined,
  DeleteOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useHistory } from 'react-router-dom';
import { Acknowledgment } from '../../services/acknowledgment';

const EditRoomsPage: FunctionComponent<{}> = () => {
  const history = useHistory();
  const { rooms, deleteRoom } = useRooms();
  const [deletingRooms, setDeletingRooms] = useState<{ [key: number]: boolean }>({});
  const [deleteErrors, setDeleteErrors] = useState<{ [key: number]: string[] }>({});

  const deleteRoomWith = (roomId: number) => {
    setDeletingRooms({ ...deletingRooms, [roomId]: true });
    deleteRoom(roomId).then(() => {
      setDeletingRooms({ ...deletingRooms, [roomId]: false })
      setDeleteErrors({ ...deleteErrors, [roomId]: [] });
    }).catch((ack: Acknowledgment) => {
      setDeletingRooms({ ...deletingRooms, [roomId]: false });
      if (ack.errors) setDeleteErrors({ ...deleteErrors, [roomId]: ack.errors });
    });
  }

  return (
    <>
      {Object.keys(deleteErrors)
        .map(roomIdErrors => deleteErrors[parseInt(roomIdErrors, 10)])
        .flat()
        .map((error, index) => (
          <>
            <Alert key={index} message={error} type="error" showIcon />
          </>
        ))}
      <List
        loading={!rooms}
        itemLayout="horizontal"
        dataSource={rooms}
        locale={{ emptyText: 'No rooms' }}
        renderItem={room => (
          <List.Item
            actions={[
              <Space>
                <Button danger shape="circle" icon={<DeleteOutlined />} loading={deletingRooms[room.id]} onClick={() => deleteRoomWith(room.id)} />
                <Button shape="circle" icon={<SettingOutlined />} disabled={deletingRooms[room.id]} onClick={() => history.push(`/rooms/${room.id}/edit`)} />
              </Space>
            ]}>
            <List.Item.Meta
              title={room.name} />
          </List.Item>
        )}
        footer={
          <List.Item
            actions={[
              <Button type="primary" shape="circle" icon={<PlusOutlined />} onClick={() => history.push('/rooms/new/edit')} />
            ]}>
            <List.Item.Meta
              title="Add new room" />
          </List.Item>
        } />
    </>
  );
}

export default EditRoomsPage;
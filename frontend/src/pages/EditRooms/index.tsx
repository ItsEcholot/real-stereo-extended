import { Button, Col, List, Row } from 'antd';
import { FunctionComponent } from 'react';
import { useRooms } from '../../services/rooms';
import { PlusOutlined } from '@ant-design/icons';
import { useHistory } from 'react-router-dom';

const EditRoomsPage: FunctionComponent<{}> = () => {
  const history = useHistory();
  const { rooms } = useRooms();

  return (
    <Row justify="center">
      <Col xl={8} lg={12} md={16} xs={24}>
        <List
          loading={!rooms}
          itemLayout="horizontal"
          dataSource={rooms}
          locale={{ emptyText: 'No rooms' }}
          renderItem={room => (
            <List.Item>
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
      </Col>
    </Row>
  );
}

export default EditRoomsPage;
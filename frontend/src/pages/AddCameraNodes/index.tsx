import { Button, List, Space } from 'antd';
import { FunctionComponent } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { useNodes } from '../../services/nodes';
import { useHistory } from 'react-router';

const AddCameraNodesPages: FunctionComponent<{}> = () => {
  const { nodes } = useNodes();
  const history = useHistory();

  const addNode = (id: number) => {
    history.push(`/nodes/${id}`);
  }

  return (
    <List
      loading={!nodes}
      itemLayout="horizontal"
      dataSource={nodes?.filter(node => !node.room)}
      locale={{ emptyText: 'No new camera nodes' }}
      renderItem={node => (
        <List.Item
          actions={[
            <Space>
              <Button type="primary" shape="circle" icon={<PlusOutlined />} onClick={() => addNode(node.id)} />
            </Space>
          ]}>
          <List.Item.Meta
            title={node.name}
            description={node.ip} />
        </List.Item>
      )} />
  );
}

export default AddCameraNodesPages;
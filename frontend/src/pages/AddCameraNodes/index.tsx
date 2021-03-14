import { Button, List, Space } from 'antd';
import { FunctionComponent } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { useNodes } from '../../services/nodes';

const AddCameraNodesPages: FunctionComponent = () => {
  const { nodes } = useNodes();

  const addNode = (id: number) => {

  }

  console.dir(nodes);

  return (
    <List
      loading={!nodes}
      itemLayout="horizontal"
      dataSource={nodes}
      locale={{ emptyText: 'No camera nodes' }}
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
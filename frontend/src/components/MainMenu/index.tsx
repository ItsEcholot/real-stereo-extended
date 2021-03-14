import { FunctionComponent } from 'react';
import { Menu } from 'antd';
import {
  HomeOutlined,
  SettingOutlined,
  PlusOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { useRooms } from '../../services/rooms';
import styles from './styles.module.css';

const { SubMenu } = Menu;

type MainMenuProps = {
  siderBroken: boolean;
  onSiderCollapse: (siderCollapsed: boolean) => void;
}

const MainMenu: FunctionComponent<MainMenuProps> = ({
  siderBroken,
  onSiderCollapse,
}) => {
  const location = useLocation();
  const { rooms } = useRooms();

  return (
    <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]}
      onSelect={() => siderBroken && onSiderCollapse(true)}
      className={styles.menu}>
      <Menu.Item key="/" icon={<HomeOutlined />}>
        <Link to="/">Overview</Link>
      </Menu.Item>
      {rooms?.map(room => (
        <SubMenu key={`submenu${room.name}`} title={room.name}>
          {room.nodes.map(node => (
            <Menu.Item key={`/nodes/${node.id}`}>
              <Link to={`/nodes/${node.id}`}>{node.name}</Link>
            </Menu.Item>
          ))}
        </SubMenu>
      ))}
      <Menu.Item key="/nodes/add" icon={<PlusOutlined />}>
        <Link to="/nodes/add">Add camera nodes</Link>
      </Menu.Item>
      <Menu.Item key="/rooms/edit" icon={<SettingOutlined />}>
        <Link to="/rooms/edit">Edit rooms</Link>
      </Menu.Item>
    </Menu>
  );
}

export default MainMenu;
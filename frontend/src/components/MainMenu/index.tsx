import { FunctionComponent } from 'react';
import { Menu } from 'antd';
import {
  HomeOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import styles from './styles.module.css';

interface MainMenuProps {
  siderBroken: boolean;
  onSiderCollapse: (siderCollapsed: boolean) => void;
}

const MainMenu: FunctionComponent<MainMenuProps> = ({
  siderBroken,
  onSiderCollapse,
}) => {
  const location = useLocation();

  return (
    <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]}
      onSelect={() => siderBroken && onSiderCollapse(true)}
      className={styles.menu}>
      <Menu.Item key="/" icon={<HomeOutlined />}>
        <Link to="/">Overview</Link>
      </Menu.Item>
      <Menu.Item key="/rooms/edit" icon={<SettingOutlined />}>
        <Link to="/rooms/edit">Edit rooms</Link>
      </Menu.Item>
    </Menu>
  );
}

export default MainMenu;
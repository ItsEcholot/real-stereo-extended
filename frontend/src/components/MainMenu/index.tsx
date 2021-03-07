import { FunctionComponent } from 'react';
import { Menu } from 'antd';
import {
  HomeOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const MainMenu: FunctionComponent<{}> = () => {
  const location = useLocation();

  return (
    <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]}>
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
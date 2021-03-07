import { FunctionComponent } from 'react';
import { Menu } from 'antd';
import {
  HomeOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';

const MainMenu: FunctionComponent<{}> = () => {
  return (
    <Menu theme="dark" mode="inline">
      <Menu.Item key="/" icon={<HomeOutlined />}>
        <Link to="/">Overview</Link>
      </Menu.Item>
      <Menu.Item key="/rooms/edit" icon={<SettingOutlined />}>
        <Link to="/rooms/edit">Edit rooms</Link>
      </Menu.Item>
      <Menu.Item key="3">
        nav 3
      </Menu.Item>
      <Menu.Item key="4">
        nav 4
      </Menu.Item>
    </Menu>
  );
}

export default MainMenu;
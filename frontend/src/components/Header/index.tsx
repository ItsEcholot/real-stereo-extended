import { FunctionComponent } from 'react';
import { Layout, Space } from 'antd';
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined
} from '@ant-design/icons';
import styles from './styles.module.css';

type HeaderProps = {
  title: string;
  siderCollapsed: boolean;
  onSiderCollapse: (siderCollapsed: boolean) => void;
}

const Header: FunctionComponent<HeaderProps> = ({
  title,
  siderCollapsed,
  onSiderCollapse: onSiderCollapseSwitch
}) => {
  return (
    <Layout.Header className={styles.header}>
      <Space size="middle">
        {siderCollapsed ?
          <MenuUnfoldOutlined onClick={() => onSiderCollapseSwitch(false)} /> :
          <MenuFoldOutlined onClick={() => onSiderCollapseSwitch(true)} />}

        <span className={styles.title}>{title}</span>
      </Space>
    </Layout.Header>
  );
}

export default Header;
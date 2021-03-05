import { FunctionComponent, useState } from 'react';
import { Layout as AntdLayout, Menu } from 'antd';
import Header from '../Header';
import styles from './styles.module.css';

const { Sider } = AntdLayout;

const Layout: FunctionComponent<{}> = props => {
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [siderBroken, setSiderBroken] = useState(false);

  return (
    <AntdLayout className={siderBroken ? (siderCollapsed ? styles.layoutSiderCollapsed : styles.layoutSiderExpanded) : ''}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        onBreakpoint={broken => {
          setSiderCollapsed(broken);
          setSiderBroken(broken);
        }}
        collapsed={siderCollapsed}
        trigger={null}>
        <Menu theme="dark" mode="inline">
          <Menu.Item key="1">
            nav 1
        </Menu.Item>
          <Menu.Item key="2">
            nav 2
        </Menu.Item>
          <Menu.Item key="3">
            nav 3
        </Menu.Item>
          <Menu.Item key="4">
            nav 4
        </Menu.Item>
        </Menu>
      </Sider>
      <AntdLayout>
        <Header siderCollapsed={siderCollapsed} onSiderCollapse={setSiderCollapsed} />
      </AntdLayout>
    </AntdLayout>
  );
}

export default Layout;
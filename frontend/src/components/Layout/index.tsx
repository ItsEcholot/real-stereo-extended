import { FunctionComponent, useState } from 'react';
import { Layout as AntdLayout } from 'antd';
import Header from '../Header';
import styles from './styles.module.css';
import MainMenu from '../MainMenu';

const { Sider, Content } = AntdLayout;

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
        trigger={null}
        className={styles.sider}>
        <MainMenu />
      </Sider>
      <AntdLayout>
        <Header siderCollapsed={siderCollapsed} onSiderCollapse={setSiderCollapsed} />
        <Content>
          {props.children}
        </Content>
      </AntdLayout>
    </AntdLayout>
  );
}

export default Layout;
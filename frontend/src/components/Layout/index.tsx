import { FunctionComponent, useState } from 'react';
import { Layout as AntdLayout, Row, Col } from 'antd';
import Header from '../Header';
import MainMenu from '../MainMenu';
import styles from './styles.module.css';

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
        <MainMenu siderBroken={siderBroken} onSiderCollapse={setSiderCollapsed} />
      </Sider>
      <AntdLayout>
        <Header title="Real Stereo" siderCollapsed={siderCollapsed} onSiderCollapse={setSiderCollapsed} />
        <Content className={styles.content}>
          <Row justify="center">
            <Col xl={8} lg={12} md={16} xs={24}>
              {props.children}
            </Col>
          </Row>
        </Content>
      </AntdLayout>
    </AntdLayout>
  );
}

export default Layout;
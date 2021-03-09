import { FunctionComponent } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Layout from './components/Layout';
import SocketProvider from './services/socketProvider';
import OverviewPage from './pages/Overview';
import EditRoomsPage from './pages/EditRooms';
import './App.css';

const App: FunctionComponent<{}> = () => {
  return (
    <SocketProvider>
      <Router>
        <Layout>
          <Switch>
            <Route path="/rooms/edit">
              <EditRoomsPage />
            </Route>
            <Route path="/">
              <OverviewPage />
            </Route>
          </Switch>
        </Layout>
      </Router>
    </SocketProvider>
  );
}

export default App;

import { FunctionComponent } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Layout from './components/Layout';
import './App.css';
import SocketProvider from './services/socketProvider';
import OverviewPage from './pages/Overview';

const App: FunctionComponent<{}> = () => {
  return (
    <SocketProvider>
      <Router>
        <Layout>
          <Switch>
            <Route path="/rooms/edit">
              <h1>Edit rooms</h1>
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

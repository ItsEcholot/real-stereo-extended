import { FunctionComponent } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Layout from './components/Layout';
import './App.css';

const App: FunctionComponent<{}> = () => {
  return (
    <Router>
      <Layout>
        <Switch>
          <Route path="/rooms/edit">
            <h1>Edit rooms</h1>
          </Route>
          <Route path="/">
            <h1>Overview</h1>
          </Route>
        </Switch>
      </Layout>
    </Router>
  );
}

export default App;

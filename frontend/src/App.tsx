import { FunctionComponent } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Layout from './components/Layout';
import SocketProvider from './services/socketProvider';
import OverviewPage from './pages/Overview';
import EditRoomsPage from './pages/EditRooms';
import EditRoomPage from './pages/EditRoom';
import AddCameraNodesPages from './pages/AddCameraNodes';
import EditNodePage from './pages/EditNode';
import './App.css';
import TestModePage from './pages/TestMode';
import CalibrateCameraPage from './pages/CalibrateCamera';

const App: FunctionComponent<{}> = () => {
  return (
    <SocketProvider>
      <Router>
        <Layout>
          <Switch>
            <Route exact path="/">
              <OverviewPage />
            </Route>
            <Route exact path="/nodes/add">
              <AddCameraNodesPages />
            </Route>
            <Route exact path="/nodes/:nodeId" render={props => (
              <EditNodePage nodeId={parseInt(props.match.params.nodeId, 10)} />
            )} />
            <Route exact path="/nodes/:nodeId/calibrate-camera" render={props => (
              <CalibrateCameraPage nodeId={parseInt(props.match.params.nodeId, 10)} />
            )} />
            <Route exact path="/rooms/edit">
              <EditRoomsPage />
            </Route>
            <Route exact path="/rooms/new/edit" >
              <EditRoomPage />
            </Route>
            <Route exact path="/rooms/:roomId/edit" render={props => (
              <EditRoomPage roomId={parseInt(props.match.params.roomId, 10)} />
            )} />
            <Route exact path="/testmode">
              <TestModePage />
            </Route>
          </Switch>
        </Layout>
      </Router>
    </SocketProvider>
  );
}

export default App;

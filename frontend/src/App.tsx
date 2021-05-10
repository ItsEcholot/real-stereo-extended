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
import SetupPage from './pages/Setup';
import RequireSetup from './components/RequireSetup';
import SetupFinishedPage from './pages/SetupFinished';

const App: FunctionComponent<{}> = () => {
  return (
    <SocketProvider>
      <Router>
        <Layout>
          <RequireSetup>
            <Switch>
              <Route exact path="/">
                <OverviewPage />
              </Route>
              <Route exact path="/setup">
                <SetupPage />
              </Route>
              <Route exact path="/setup/finished/:nodeType" render={props => (
                <SetupFinishedPage nodeType={props.match.params.nodeType as 'master' | 'tracking'} />
              )} />
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
          </RequireSetup>
        </Layout>
      </Router>
    </SocketProvider>
  );
}

export default App;

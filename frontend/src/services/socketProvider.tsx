import { createContext, FunctionComponent } from 'react';
import io from 'socket.io-client';

const baseSocketUrl = process.env.NODE_ENV !== 'production' && process.env.REACT_APP_BACKEND_URL ? process.env.REACT_APP_BACKEND_URL : '';

const sockets: { [key: string]: SocketIOClient.Socket } = {};
const socketsReferences: { [key: string]: number } = {};

const getSocket = (namespace: string) => {
  if (!sockets[namespace]) {
    sockets[namespace] = io(`${baseSocketUrl}/${namespace}`, {
      rejectUnauthorized: false,
    });
    console.debug(`Creating socket /${namespace}`);
  }
  if (!socketsReferences[namespace]) {
    socketsReferences[namespace] = 0;
  }
  socketsReferences[namespace]++;
  console.debug(`Getting socket /${namespace} has now ${socketsReferences[namespace]} references`);
  console.debug(`Currently open sockets: ${Object.keys(sockets)}`)
  return sockets[namespace];
};
const returnSocket = (namespace: string) => {
  socketsReferences[namespace]--;
  console.debug(`Returning socket /${namespace} has now ${socketsReferences[namespace]} references`);
  if (socketsReferences[namespace] === 0) {
    console.debug(`Disconnecting socket /${namespace}`);
    sockets[namespace].disconnect();
    delete sockets[namespace];
  }
  console.debug(`Currently open sockets: ${Object.keys(sockets)}`)
}

export const SocketContext = createContext({
  getSocket,
  returnSocket,
});

const SocketProvider: FunctionComponent<{}> = ({ children }) => {
  return (
    <SocketContext.Provider value={{
      getSocket,
      returnSocket,
    }}>
      {children}
    </SocketContext.Provider>
  );
}

export default SocketProvider;
import { createContext, FunctionComponent } from 'react';
import io from 'socket.io-client';

const baseSocketUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8080' : '';

const sockets: { [key: string]: SocketIOClient.Socket } = {};
const socketsReferences: { [key: string]: number } = {};

const getSocket = (namespace: string) => {
  if (!sockets[namespace]) {
    sockets[namespace] = io(`${baseSocketUrl}/${namespace}`);
    console.log(`Creating socket /${namespace}`);
  }
  if (!socketsReferences[namespace]) {
    socketsReferences[namespace] = 0;
  }
  socketsReferences[namespace]++;
  console.log(`Getting socket /${namespace}`);
  console.log(`Socket ${namespace} has ${socketsReferences[namespace]} references`);
  return sockets[namespace];
};
const returnSocket = (namespace: string) => {
  socketsReferences[namespace]--;
  console.log(`Returning socket /${namespace}`);
  console.log(`Socket ${namespace} has ${socketsReferences[namespace]} references`);
  if (socketsReferences[namespace] === 0) {
    console.log(`Disconnecting socket /${namespace}`);
    sockets[namespace].disconnect();
    delete sockets[namespace];
  }
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
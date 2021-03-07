import { createContext, FunctionComponent } from 'react';
import io from 'socket.io-client';

const baseSocketUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8080' : '';
const roomsSocket = io(`${baseSocketUrl}/rooms`);
export const SocketContext = createContext({
  roomsSocket
});

const SocketProvider: FunctionComponent<{}> = ({ children }) => {
  return (
    <SocketContext.Provider value={{
      roomsSocket,
    }}>
      {children}
    </SocketContext.Provider>
  );
}

export default SocketProvider;
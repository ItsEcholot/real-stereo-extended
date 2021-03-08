import { useCallback, useContext, useEffect, useState } from 'react';
import { SocketContext } from './socketProvider';

export interface Room {
  id: number;
  name: string;
  nodes: any[];
  speakers: any[];
}

export const useRooms = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [rooms, setRooms] = useState<Room[]>([]);
  useEffect(() => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.on('get', setRooms);
    return () => {
      roomsSocket.off('get', setRooms);
      returnSocket('rooms');
    };
  }, [getSocket, returnSocket]);

  const createRoom = useCallback((room: Omit<Room, 'id'>) => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.emit('create', room);
    returnSocket('rooms');
  }, [getSocket, returnSocket]);

  const updateRoom = useCallback((roomId: number, room: Partial<Room>) => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.emit('update', roomId, room);
    returnSocket('rooms');
  }, [getSocket, returnSocket]);

  const deleteRoom = useCallback((roomId: number) => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.emit('delete', roomId);
    returnSocket('rooms');
  }, [getSocket, returnSocket]);

  return { rooms, createRoom, updateRoom, deleteRoom };
}
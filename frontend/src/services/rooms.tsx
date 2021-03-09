import { useCallback, useContext, useEffect, useState } from 'react';
import { Node } from './nodes';
import { SocketContext } from './socketProvider';

export type Room = {
  id: number;
  name: string;
  nodes: Node[];
}

export type UpdateRoom = Omit<Room, 'nodes'>
export type CreateRoom = Omit<UpdateRoom, 'id'>

export const useRooms = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [rooms, setRooms] = useState<Room[]>();
  useEffect(() => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.on('get', setRooms);
    roomsSocket.emit('get');
    return () => {
      roomsSocket.off('get', setRooms);
      returnSocket('rooms');
    };
  }, [getSocket, returnSocket]);

  const createRoom = useCallback((room: CreateRoom) => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.emit('create', room);
    returnSocket('rooms');
  }, [getSocket, returnSocket]);

  const updateRoom = useCallback((room: UpdateRoom) => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.emit('update', room);
    returnSocket('rooms');
  }, [getSocket, returnSocket]);

  const deleteRoom = useCallback((roomId: number) => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.emit('delete', roomId);
    returnSocket('rooms');
  }, [getSocket, returnSocket]);

  return { rooms, createRoom, updateRoom, deleteRoom };
}
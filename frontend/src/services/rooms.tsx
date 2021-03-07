import { useCallback, useContext, useEffect, useState } from 'react';
import { SocketContext } from './socketProvider';

export interface Room {
  id: number;
  name: string;
  nodes: any[];
  speakers: any[];
}

export const useRooms = () => {
  const { roomsSocket } = useContext(SocketContext);
  const [rooms, setRooms] = useState<Room[]>([]);
  useEffect(() => {
    roomsSocket.on('get', setRooms);
    return () => {
      roomsSocket.off('get', setRooms);
    };
  }, [roomsSocket]);

  const createRoom = useCallback((room: Omit<Room, 'id'>) => {
    roomsSocket.emit('create', room);
  }, [roomsSocket]);

  const updateRoom = useCallback((roomId: number, room: Partial<Room>) => {
    roomsSocket.emit('update', roomId, room);
  }, [roomsSocket]);

  const deleteRoom = useCallback((roomId: number) => {
    roomsSocket.emit('delete', roomId);
  }, [roomsSocket]);

  return { rooms, createRoom, updateRoom, deleteRoom };
}
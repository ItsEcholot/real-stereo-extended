import { useContext, useEffect, useState } from 'react';
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

  return rooms;
}
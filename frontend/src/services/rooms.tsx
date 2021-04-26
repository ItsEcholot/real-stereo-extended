import { useCallback, useContext, useEffect, useState } from 'react';
import { Node } from './nodes';
import { SocketContext } from './socketProvider';
import { Acknowledgment } from './acknowledgment';

export type Room = {
  id: number;
  name: string;
  nodes: Omit<Node, 'room'>[];
  people_group?: string;
}

export type UpdateRoom = Omit<Room, 'nodes'>
export type CreateRoom = Omit<UpdateRoom, 'id'>

export const useRooms = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [rooms, setRooms] = useState<Room[]>();
  useEffect(() => {
    const roomsSocket = getSocket('rooms');
    roomsSocket.emit('get', setRooms);
    roomsSocket.on('get', setRooms);
    return () => {
      roomsSocket.off('get', setRooms);
      returnSocket('rooms');
    };
  }, [getSocket, returnSocket]);

  const createRoom = useCallback((room: CreateRoom): Promise<Acknowledgment> => {
    const roomsSocket = getSocket('rooms');
    return new Promise((resolve, reject) => {
      roomsSocket.emit('create', room, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('rooms');
      });
    });
  }, [getSocket, returnSocket]);

  const updateRoom = useCallback((room: UpdateRoom): Promise<Acknowledgment> => {
    const roomsSocket = getSocket('rooms');
    return new Promise((resolve, reject) => {
      roomsSocket.emit('update', room, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('rooms');
      });
    });
  }, [getSocket, returnSocket]);

  const deleteRoom = useCallback((roomId: number): Promise<Acknowledgment> => {
    const roomsSocket = getSocket('rooms');
    return new Promise((resolve, reject) => {
      roomsSocket.emit('delete', roomId, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('rooms');
      });
    });
  }, [getSocket, returnSocket]);

  return { rooms, createRoom, updateRoom, deleteRoom };
}

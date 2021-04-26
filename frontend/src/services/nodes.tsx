import { useCallback, useContext, useEffect, useState } from 'react';
import { Acknowledgment } from './acknowledgment';
import { Room } from './rooms';
import { SocketContext } from './socketProvider';

export type Node = {
  id: number;
  name: string;
  online: boolean;
  ip: string;
  hostname: string;
  room: Omit<Room, 'nodes'>;
  detector?: string;
}

export type UpdateNode = {
  id: number;
  name: string;
  ip: string;
  // only the `id` attribute of the room is needed
  // more can still be submitted but will be ignored
  room: {
    id: number;
  };
  detector?: string;
}

export const useNodes = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [nodes, setNodes] = useState<Node[]>();
  useEffect(() => {
    const nodesSocket = getSocket('nodes');
    nodesSocket.emit('get', setNodes);
    nodesSocket.on('get', setNodes);
    return () => {
      nodesSocket.off('get', setNodes);
      returnSocket('nodes');
    };
  }, [getSocket, returnSocket]);

  const updateNode = useCallback((node: UpdateNode): Promise<Acknowledgment> => {
    const nodesSocket = getSocket('nodes');
    return new Promise((resolve, reject) => {
      nodesSocket.emit('update', node, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('nodes');
      });
    });
  }, [getSocket, returnSocket]);

  const deleteNode = useCallback((nodeId: number): Promise<Acknowledgment> => {
    const nodesSocket = getSocket('nodes');
    return new Promise((resolve, reject) => {
      nodesSocket.emit('delete', nodeId, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('nodes');
      });
    });
  }, [getSocket, returnSocket]);

  return { nodes, updateNode, deleteNode };
}

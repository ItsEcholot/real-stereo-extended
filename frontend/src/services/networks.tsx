import { useCallback, useContext } from 'react';
import { Acknowledgment } from './acknowledgment';
import { SocketContext } from './socketProvider';

export type CreateNetwork = {
  ssid: string;
  psk?: string;
};

export const useNetworks = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);

  const createNetwork = useCallback((network: CreateNetwork): Promise<Acknowledgment> => {
    const networksSocket = getSocket('networks');
    return new Promise((resolve, reject) => {
      networksSocket.emit('create', network, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('networks');
      })
    });
  }, [getSocket, returnSocket]);

  return { createNetwork };
};

import { useContext, useState, useEffect, useCallback } from 'react';
import { Acknowledgment } from './acknowledgment';
import { CreateNetwork } from './networks';
import { SocketContext } from './socketProvider';

export type Settings = {
  configured: boolean;
  balance: boolean;
  network: 'client' | 'adhoc';
}

export type UpdateSettings = {
  balance: boolean;
  nodeType?: 'master' | 'tracking';
  network?: CreateNetwork;
}

export const useSettings = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [settings, setSettings] = useState<Settings>();
  useEffect(() => {
    const settingsSocket = getSocket('settings');
    settingsSocket.emit('get', setSettings);
    settingsSocket.on('get', setSettings);
    return () => {
      settingsSocket.off('get', setSettings);
      returnSocket('settings');
    };
  }, [getSocket, returnSocket]);

  const updateSettings = useCallback((settings: UpdateSettings): Promise<Acknowledgment> => {
    const settingsSocket = getSocket('settings');
    return new Promise((resolve, reject) => {
      settingsSocket.emit('update', settings, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('settings');
      });
    });
  }, [getSocket, returnSocket]);

  return { settings, updateSettings };
}

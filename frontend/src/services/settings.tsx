import { useContext, useState, useEffect, useCallback } from 'react';
import { Acknowledgment } from './acknowledgment';
import { Room } from './rooms';
import { SocketContext } from './socketProvider';

export type Settings = {
  configured: boolean;
  balance: boolean;
  testMode: boolean;
}

export type UpdateSettings = {
  balance?: boolean;
  testMode?: boolean;
}

export type SettingsTestModeResult = {
  room: Room;
  positionX: number;
  positionY: number;
}

export const useSettings = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [settings, setSettings] = useState<Settings>();
  const [settingsTestModeResult, setSettingsTestModeResult] = useState<SettingsTestModeResult[]>();
  useEffect(() => {
    const settingsSocket = getSocket('settings');
    settingsSocket.emit('get', setSettings);
    settingsSocket.on('get', setSettings);
    settingsSocket.on('testModeResult', setSettingsTestModeResult);
    return () => {
      settingsSocket.off('get', setSettings);
      settingsSocket.off('testModeResult', setSettingsTestModeResult);
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

  return { settings, settingsTestModeResult, updateSettings };
}
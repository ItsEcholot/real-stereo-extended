import { useContext, useState, useEffect, useCallback } from 'react';
import { Acknowledgment } from './acknowledgment';
import { Room } from './rooms';
import { SocketContext } from './socketProvider';

export type Speaker = {
  id: string;
  name: string;
  room: Omit<Room, 'speakers'>;
}

export type UpdateSpeaker = {
  id: string;
  name: string;
  // only the `id` attribute of the room is needed
  // more can still be submitted but will be ignored
  room: Partial<Room> & {
    id: number;
  };
}

export const useSpeakers = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [speakers, setSpeakers] = useState<Speaker[]>();
  useEffect(() => {
    const speakersSocket = getSocket('speakers');
    speakersSocket.emit('get', setSpeakers);
    speakersSocket.on('get', setSpeakers);
    return () => {
      speakersSocket.off('get', setSpeakers);
      returnSocket('speakers');
    };
  }, [getSocket, returnSocket]);

  const updateSpeaker = useCallback((speaker: UpdateSpeaker): Promise<Acknowledgment> => {
    const speakersSocket = getSocket('speakers');
    return new Promise((resolve, reject) => {
      speakersSocket.emit('update', speaker, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('speakers');
      });
    });
  }, [getSocket, returnSocket]);

  const deleteSpeaker = useCallback((speakerId: string): Promise<Acknowledgment> => {
    const speakersSocket = getSocket('speakers');
    return new Promise((resolve, reject) => {
      speakersSocket.emit('delete', speakerId, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('speakers');
      });
    });
  }, [getSocket, returnSocket]);

  return { speakers, updateSpeaker, deleteSpeaker };
}
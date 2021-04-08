import { useCallback, useContext, useEffect, useState } from 'react';
import { SocketContext } from './socketProvider';
import { Acknowledgment } from './acknowledgment';

export type RoomCalibrationRequest = {
  room: {
    id: number;
  };
  start?: boolean;
  finish?: boolean;
  repeatPoint?: boolean;
  nextPoint?: boolean;
  nextSpeaker?: boolean;
}

export type RoomCalibrationResponse = {
  room: {
    id: number;
  };
  calibrating: boolean;
  positionX: number;
  positionY: number;
  noiseDone?: true;
}

export type RoomCalibrationResult = {
  room: {
    id: number;
  };
  volume: number;
}

export const useRoomCalibration = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [roomId, setRoomId] = useState<number>();
  const [roomCalibration, setRoomCalibration] = useState<RoomCalibrationResponse>();

  const setRoomCalibrationForRoom = useCallback((roomCalibration: RoomCalibrationResponse) => {
    if (roomCalibration.room.id === roomId) {
      setRoomCalibration(roomCalibration);
    }
  }, [roomId]);

  useEffect(() => {
    if (!roomId) return;
    const calibrationSocket = getSocket('room-calibration');
    calibrationSocket.on('get', setRoomCalibrationForRoom);
    calibrationSocket.emit('update', {
      room: {id: roomId}
    });
    return () => {
      calibrationSocket.off('get', setRoomCalibrationForRoom);
      returnSocket('room-calibration');
    };
  }, [getSocket, returnSocket, setRoomCalibrationForRoom, roomId]);

  const startCalibration = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket('room-calibration');
    return new Promise((resolve, reject) => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        start: true,
      }, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('room-calibration');
      })
    });
  }, [getSocket, returnSocket, roomId]);

  return { roomCalibration, setRoomId, startCalibration };
};
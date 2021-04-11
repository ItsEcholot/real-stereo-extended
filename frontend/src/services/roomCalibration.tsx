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
  const socketRoomName = 'room-calibration';
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [roomId, setRoomId] = useState<number>();
  const [roomCalibration, setRoomCalibration] = useState<RoomCalibrationResponse>();
  const [errors, setErrors] = useState<string[]>([]);

  const setRoomCalibrationForRoom = useCallback((roomCalibration: RoomCalibrationResponse) => {
    if (roomCalibration.room.id === roomId) {
      setRoomCalibration(roomCalibration);
    }
  }, [roomId]);

  useEffect(() => {
    if (!roomId) return;
    const calibrationSocket = getSocket(socketRoomName);
    calibrationSocket.on('get', setRoomCalibrationForRoom);
    calibrationSocket.emit('update', {
      room: {id: roomId}
    });
    return () => {
      calibrationSocket.off('get', setRoomCalibrationForRoom);
      returnSocket(socketRoomName);
    };
  }, [getSocket, returnSocket, setRoomCalibrationForRoom, roomId]);

  const startCalibration = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise((resolve, reject) => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        start: true,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        resolve(ack);
        returnSocket(socketRoomName);
      })
    });
  }, [getSocket, returnSocket, roomId]);

  const finishCalibration = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise((resolve, reject) => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        finish: true,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        resolve(ack);
        returnSocket(socketRoomName);
      })
    });
  }, [getSocket, returnSocket, roomId]);

  return { roomCalibration, errors, setRoomId, startCalibration, finishCalibration };
};
import { RefObject, useCallback, useContext, useEffect, useState } from 'react';
import { SocketContext } from './socketProvider';
import { Acknowledgment } from './acknowledgment';
import { useAudioMeter, prepareAudioMeter, medianHistoricVolume } from './audioMeter';
import { drawCurrentPosition, drawInterpolation, drawPoints, mapCoordinate } from './canvasDrawTools';

export type RoomCalibrationRequest = {
  room: {
    id: number;
  };
  start?: boolean;
  startVolume?: number;
  finish?: boolean;
  repeatPoint?: boolean;
  confirmPoint?: boolean;
  nextPoint?: boolean;
  nextSpeaker?: boolean;
}

export type RoomCalibrationPoint = {
  coordinateX: number;
  coordinateY: number;
  measuredVolume: number;
  speaker_id: string;
}

export type RoomCalibrationResponse = {
  room: {
    id: number;
  };
  calibrating: boolean;
  positionX: number;
  positionY: number;
  positionFreeze: boolean;
  currentSpeakerIndex: number,
  currentPoints: RoomCalibrationPoint[],
  previousPoints: RoomCalibrationPoint[],
}

export type RoomCalibrationResult = {
  room: {
    id: number;
  };
  volume: number;
}

const canvasSize = 250;

export const useRoomCalibration = (roomId: number, calibrationMapCanvasRef: RefObject<HTMLCanvasElement> | null = null, selectedCalibrationMapSpeakerId: string) => {
  const socketRoomName = 'room-calibration';
  const { getSocket, returnSocket } = useContext(SocketContext);

  const [roomCalibration, setRoomCalibration] = useState<RoomCalibrationResponse>();
  const [errors, setErrors] = useState<string[]>([]);
  const [measuringVolume, setMeasuringVolume] = useState(false);
  const [nextSpeakerTimeout, setNextSpeakerTimeout] = useState<NodeJS.Timeout>();

  const { audioMeterErrors, volume } = useAudioMeter(measuringVolume);

  const setRoomCalibrationForRoom = useCallback((roomCalibration: RoomCalibrationResponse) => {
    if (roomCalibration.room.id === roomId) {
      setRoomCalibration(roomCalibration);

      const context = calibrationMapCanvasRef?.current?.getContext("2d");
      if (context) {
        context.clearRect(0, 0, canvasSize, canvasSize);
        
        const speakerIdSet: Set<string> = new Set();
        roomCalibration.previousPoints.forEach(previousPoint => speakerIdSet.add(previousPoint.speaker_id));
        drawInterpolation(context, canvasSize, roomCalibration.previousPoints.filter(prevPoint => prevPoint.speaker_id === selectedCalibrationMapSpeakerId), Array.from(speakerIdSet).indexOf(selectedCalibrationMapSpeakerId));
        drawPoints(context, canvasSize, roomCalibration.previousPoints, '#555555');
        drawPoints(context, canvasSize, roomCalibration.currentPoints, '#000000');
        drawCurrentPosition(context, canvasSize, mapCoordinate(roomCalibration.positionX, canvasSize), mapCoordinate(roomCalibration.positionY, canvasSize));
      }
    }
  }, [roomId, calibrationMapCanvasRef, selectedCalibrationMapSpeakerId]);

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
  }, [getSocket, returnSocket, setRoomCalibrationForRoom, roomId, calibrationMapCanvasRef]);

  useEffect(() => {
    if (calibrationMapCanvasRef && calibrationMapCanvasRef.current) {
      calibrationMapCanvasRef.current.width = canvasSize;
      calibrationMapCanvasRef.current.height = canvasSize;
      const context = calibrationMapCanvasRef.current.getContext("2d");
      if (context) {
        context.clearRect(0, 0, canvasSize, canvasSize);
      }
    }
  }, [roomCalibration?.calibrating, calibrationMapCanvasRef])

  const prepareCalibration = useCallback((): void => {
    prepareAudioMeter();
  }, []);

  const startCalibration = useCallback((startVolume: number): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise(resolve => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        start: true,
        startVolume,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        resolve(ack);
        returnSocket(socketRoomName);
      });
    });
  }, [getSocket, returnSocket, roomId]);

  const finishCalibration = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise(resolve => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        finish: true,
      }, (ack: Acknowledgment) => {
        if (nextSpeakerTimeout) {
          clearTimeout(nextSpeakerTimeout);
          setNextSpeakerTimeout(undefined);
        }
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        setTimeout(() => setErrors([]), 3000);
        resolve(ack);
        returnSocket(socketRoomName);
      });
    });
  }, [getSocket, returnSocket, roomId, nextSpeakerTimeout]);

  const nextPoint = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise(resolve => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        nextPoint: true,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        resolve(ack);
        returnSocket(socketRoomName);
      });
    });
  }, [getSocket, returnSocket, roomId]);

  const nextSpeaker = useCallback((record: boolean = true): Promise<Acknowledgment> | undefined => {
    const calibrationSocket = getSocket(socketRoomName);

    return new Promise(resolve => {
      calibrationSocket.emit('update', {
        room: {id: roomId},
        nextSpeaker: true,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
          resolve(ack);
          returnSocket(socketRoomName);
        } else if (record) {
          setMeasuringVolume(true);
          setNextSpeakerTimeout(setTimeout(() => {
            const medianVolume = medianHistoricVolume();
            console.debug(`Calibration measured average volume: ${medianVolume}`);
            calibrationSocket.emit('result', {
              room: {id: roomId},
              volume: medianVolume
            }, (ack: Acknowledgment) => {
              if (!ack.successful && ack.errors !== undefined) {
                const ackErrors = ack.errors;
                setErrors(prevErrors => [...prevErrors, ...ackErrors])
              }
              resolve(ack);
              returnSocket(socketRoomName);
            });
            setMeasuringVolume(false);
          }, 5000));
        } else {
          resolve(ack);
          returnSocket(socketRoomName);
        }
      });
    });
  }, [getSocket, returnSocket, roomId]);

  const confirmPoint = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise(resolve => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        confirmPoint: true,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        resolve(ack);
        returnSocket(socketRoomName);
      });
    });
  }, [getSocket, returnSocket, roomId]);

  const repeatPoint = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise(resolve => {    
      calibrationSocket.emit('update', {
        room: {id: roomId},
        repeatPoint: true,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        resolve(ack);
        returnSocket(socketRoomName);
      });
    });
  }, [getSocket, returnSocket, roomId]);

  return { 
    roomCalibration,
    errors,
    audioMeterErrors,
    prepareCalibration,
    startCalibration,
    finishCalibration,
    nextPoint,
    nextSpeaker,
    confirmPoint,
    repeatPoint,
    volume,
  };
};
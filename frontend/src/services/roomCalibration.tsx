import { RefObject, useCallback, useContext, useEffect, useState } from 'react';
import { SocketContext } from './socketProvider';
import { Acknowledgment } from './acknowledgment';
import { useAudioMeter, historicVolume, prepareAudioMeter } from './audioMeter';

export type RoomCalibrationRequest = {
  room: {
    id: number;
  };
  start?: boolean;
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

const canvasCordSize = 100;
const maxCord = 640;

const mapCoordinate = (cord: number): number => {
  // Remove aliasing using +0.5
  return Math.round((cord / maxCord) * canvasCordSize) + 0.5;
}

const drawCurrentPosition = (context: CanvasRenderingContext2D, x: number, y: number) => {
  const crosshairRadius = 3;
  context.strokeStyle = '#ff0000';
  context.beginPath();
  context.moveTo(x - crosshairRadius, y);
  context.lineTo(x + crosshairRadius, y);
  context.moveTo(x, y - crosshairRadius);
  context.lineTo(x, y + crosshairRadius);
  context.stroke();
}

const drawPoints = (context: CanvasRenderingContext2D, previousPoints: RoomCalibrationPoint[], fillStyle: string) => {
  const pointRadius = 2;
  context.fillStyle = fillStyle;
  context.beginPath();
  for (const point of previousPoints) {
    context.arc(mapCoordinate(point.coordinateX), mapCoordinate(point.coordinateY), pointRadius, 0, 2 * Math.PI);
    context.fill();
  }
}

export const useRoomCalibration = (roomId: number, calibrationMapCanvasRef: RefObject<HTMLCanvasElement> | null = null) => {
  const socketRoomName = 'room-calibration';
  const { getSocket, returnSocket } = useContext(SocketContext);

  const [roomCalibration, setRoomCalibration] = useState<RoomCalibrationResponse>();
  const [errors, setErrors] = useState<string[]>([]);
  const [measuringVolume, setMeasuringVolume] = useState(false);

  const { audioMeterErrors, volume } = useAudioMeter(measuringVolume);

  const setRoomCalibrationForRoom = useCallback((roomCalibration: RoomCalibrationResponse) => {
    if (roomCalibration.room.id === roomId) {
      setRoomCalibration(roomCalibration);
      console.dir(roomCalibration);

      const context = calibrationMapCanvasRef?.current?.getContext("2d");
      if (context) {
        context.clearRect(0, 0, canvasCordSize, canvasCordSize);
        drawPoints(context, roomCalibration.previousPoints, '#555555');
        drawPoints(context, roomCalibration.currentPoints, '#000000');
        drawCurrentPosition(context, mapCoordinate(roomCalibration.positionX), mapCoordinate(roomCalibration.positionY));
      }
    }
  }, [roomId, calibrationMapCanvasRef]);

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
      calibrationMapCanvasRef.current.width = canvasCordSize;
      calibrationMapCanvasRef.current.height = canvasCordSize;
      const context = calibrationMapCanvasRef.current.getContext("2d");
      if (context) {
        context.clearRect(0, 0, canvasCordSize, canvasCordSize);
      }
    }
  }, [roomCalibration?.calibrating, calibrationMapCanvasRef])

  const prepareCalibration = useCallback((): void => {
    prepareAudioMeter();
  }, []);

  const startCalibration = useCallback((): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket(socketRoomName);
    return new Promise(resolve => {    
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
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        }
        setTimeout(() => setErrors([]), 3000);
        resolve(ack);
        returnSocket(socketRoomName);
      });
    });
  }, [getSocket, returnSocket, roomId]);

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
          setTimeout(() => {
            historicVolume.sort();
            const length = historicVolume.length;
            const mid = Math.ceil(length / 2);
            //const averageVolume = historicVolume.reduce((acc, volume) => acc + volume) / historicVolume.length;
            const medianVolume = length % 2 === 0 ? (historicVolume[mid] + historicVolume[mid - 1]) / 2 : historicVolume[mid - 1];
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
          }, 5000);
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
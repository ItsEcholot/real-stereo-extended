import { RefObject, useCallback, useContext, useEffect, useState } from 'react';
import { SocketContext } from './socketProvider';
import { Acknowledgment } from './acknowledgment';
import { useAudioMeter } from './audioMeter';
import { useSpeakers } from './speakers';

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

export type RoomCalibrationPoint = {
  coordinateX: number;
  coordinateY: number;
  measuredVolumeLow: number;
  measuredVolumeHigh: number;
}

export type RoomCalibrationResponse = {
  room: {
    id: number;
  };
  calibrating: boolean;
  positionX: number;
  positionY: number;
  noiseDone: boolean;
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

const drawCurrentPosition = (context: CanvasRenderingContext2D, x: number, y: number) => {
  x = Math.round(x / 10);
  y = Math.round(y / 10); // TODO: This can be removed when/if we use the same scaling as the old (100:100 coordinates)
  const crosshairRadius = 3;
  context.strokeStyle = '#ff0000';
  context.beginPath();
  context.moveTo(x - crosshairRadius, y);
  context.lineTo(x + crosshairRadius, y);
  context.moveTo(x, y - crosshairRadius);
  context.lineTo(x, x + crosshairRadius);
  context.stroke();
}

export const useRoomCalibration = (roomId: number, calibrationMapCanvasRef: RefObject<HTMLCanvasElement> | null = null) => {
  const socketRoomName = 'room-calibration';
  const canvasCordSize = 100;
  const { getSocket, returnSocket } = useContext(SocketContext);

  const [roomCalibration, setRoomCalibration] = useState<RoomCalibrationResponse>();
  const [errors, setErrors] = useState<string[]>([]);
  const [measuringVolume, setMeasuringVolume] = useState(false);

  const { speakers } = useSpeakers();
  const { historicVolume, audioMeterErrors } = useAudioMeter(measuringVolume);

  const setRoomCalibrationForRoom = useCallback((roomCalibration: RoomCalibrationResponse) => {
    if (roomCalibration.room.id === roomId) {
      setRoomCalibration(roomCalibration);

      const context = calibrationMapCanvasRef?.current?.getContext("2d");
      if (context) {
        context.clearRect(0, 0, canvasCordSize, canvasCordSize);
        drawCurrentPosition(context, roomCalibration.positionX, roomCalibration.positionY);
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
        context.fillStyle = '#000000';
      }
    }
  }, [roomCalibration?.calibrating, calibrationMapCanvasRef])

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

  const nextPosition = useCallback((): Promise<Acknowledgment> => {
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

  const nextSpeaker = useCallback((): Promise<Acknowledgment> | undefined => {
    if (!roomCalibration || !speakers) return;
    const calibrationSocket = getSocket(socketRoomName);

    const afterVolumeMeasurement = () => {
      setMeasuringVolume(false);
      if (historicVolume.length > 0) {
        const averageVolume = historicVolume.reduce((acc, volume) => acc + volume) / historicVolume.length;
      }
      // TODO: Send result to backend
      nextSpeaker();
    };

    return new Promise(resolve => {
      calibrationSocket.emit('update', {
        room: {id: roomId},
        nextSpeaker: true,
      }, (ack: Acknowledgment) => {
        if (!ack.successful && ack.errors !== undefined) {
          const ackErrors = ack.errors;
          setErrors(prevErrors => [...prevErrors, ...ackErrors])
        } else {
          if (roomCalibration.currentSpeakerIndex + 1 < speakers.filter(speaker => speaker.room.id === roomId).length - 1) {
            setMeasuringVolume(true);
            setTimeout(afterVolumeMeasurement, 5000);
          }
        }
        resolve(ack);
        returnSocket(socketRoomName);
      });
    });
  }, [getSocket, returnSocket, roomId, roomCalibration, speakers, historicVolume]);

  return { 
    roomCalibration,
    errors,
    startCalibration,
    finishCalibration,
    nextPosition,
    nextSpeaker,
  };
};
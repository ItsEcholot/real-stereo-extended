import { useCallback, useContext, useEffect, useState } from 'react';
import { Acknowledgment } from './acknowledgment';
import { SocketContext } from './socketProvider';

export type CameraCalibrationRequest = {
  node: {
    id: number;
  };
  start?: boolean;
  finish?: boolean;
  repeat?: boolean;
}

export type CameraCalibrationResponse = {
  node: {
    id: number;
  };
  count: number;
  image: string;
}

export const useCameraCalibration = (nodeId?: number) => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [cameraCalibration, setCameraCalibration] = useState<CameraCalibrationResponse>();

  const setCameraCalibrationForNode = useCallback((cameraCalibration: CameraCalibrationResponse) => {
    if (cameraCalibration.node.id === nodeId) {
      setCameraCalibration(cameraCalibration);
    }
  }, [nodeId]);

  useEffect(() => {
    const calibrationSocket = getSocket('camera-calibration');
    calibrationSocket.on('get', setCameraCalibrationForNode);
    return () => {
      calibrationSocket.off('get', setCameraCalibrationForNode);
      returnSocket('camera-calibration');
    };
  }, [getSocket, returnSocket, setCameraCalibrationForNode]);

  const updateCameraCalibration = useCallback((cameraCalibration: Partial<CameraCalibrationRequest>): Promise<Acknowledgment> => {
    const calibrationSocket = getSocket('camera-calibration');
    return new Promise((resolve, reject) => {
      calibrationSocket.emit('update', {
        node: { id: nodeId },
        ...cameraCalibration,
      }, (ack: Acknowledgment) => {
        if (ack.successful) resolve(ack);
        else reject(ack);
        returnSocket('camera-calibration');
      })
    });
  }, [getSocket, returnSocket, nodeId]);

  return { cameraCalibration, updateCameraCalibration };
};
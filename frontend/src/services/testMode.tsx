import { RefObject, useCallback, useEffect, useState } from "react";
import { disableHistoricVolume, enableHistoricVolume, medianHistoricVolume } from "./audioMeter";
import { drawCurrentPosition, getRandomHexColourString, mapCoordinate } from "./canvasDrawTools";
import { SettingsTestModeResult, useSettings } from "./settings";

const testModeMapCanvasSize = 500;

type TestPoint = {
  roomId: number;
  positionX: number;
  positionY: number;
  volume: number;
}

export const useTestMode = (enabled: boolean, balance: boolean, testModeSpeaker: string | null = null, testModeMapCanvasRef: RefObject<HTMLCanvasElement> | null = null, mapCanvasRoomId: number | null = null) => {
  const { settingsTestModeResult, updateSettings } = useSettings();

  const [errors, setErrors] = useState<string[]>([]);
  const [readyToTestLocation, setReadyToTestLocation] = useState(false);
  const [testPoints, setTestPoints] = useState<TestPoint[]>([]);

  const drawTestModeMap = useCallback((result: SettingsTestModeResult | undefined) => {
    const testModeMapContext = testModeMapCanvasRef?.current?.getContext('2d');
    if (testModeMapContext) {
      testModeMapContext.clearRect(0, 0, testModeMapCanvasSize, testModeMapCanvasSize);
      if (result) {
        testModeMapContext.font = `${0.08 * testModeMapCanvasSize}px sans-serif`;
        testModeMapContext.textAlign = 'center';
        testModeMapContext.textBaseline = 'middle';
        testPoints.filter(testPoint => testPoint.roomId === mapCanvasRoomId).forEach(testPoint => {
          testModeMapContext.beginPath();
          testModeMapContext.fillStyle = getRandomHexColourString(0, testPoint.volume);
          const mappedX = mapCoordinate(testPoint.positionX, testModeMapCanvasSize);
          const mappedY = mapCoordinate(testPoint.positionY, testModeMapCanvasSize);
          testModeMapContext.arc(
            mappedX,
            mappedY,
            0.05 * testModeMapCanvasSize,
            0,
            Math.PI * 2
          );
          testModeMapContext.fill();
          testModeMapContext.fillStyle = '#ffffff';
          testModeMapContext.fillText(`${Math.round(testPoint.volume)}`, mappedX, mappedY);
        });

        drawCurrentPosition(
          testModeMapContext,
          testModeMapCanvasSize,
          mapCoordinate(result.positionX, testModeMapCanvasSize),
          mapCoordinate(result.positionY, testModeMapCanvasSize)
        );
      }
    }
  }, [testModeMapCanvasRef, mapCanvasRoomId, testPoints]);

  useEffect(() => {
    (async () => {
      if (testModeMapCanvasRef && testModeMapCanvasRef.current) {
        testModeMapCanvasRef.current.width = 500;
        testModeMapCanvasRef.current.height = 500;
        const testModeMapContext = testModeMapCanvasRef.current.getContext('2d');
        if (testModeMapContext) {
          testModeMapContext.clearRect(0, 0, testModeMapCanvasSize, testModeMapCanvasSize);
        }
      }

      try {
        if (enabled) {
          await updateSettings({ testMode: true, balance, testModeSpeaker: testModeSpeaker || undefined });
          disableHistoricVolume();
          setReadyToTestLocation(true);
        } else {
          await updateSettings({ testMode: false });
        }
      } catch (ack) {
        setErrors(prevErr => [...prevErr, ...ack.errors])
      }
    })();

    return () => {
      updateSettings({ testMode: false, balance: false });
      setTestPoints([]);
    }
  }, [enabled, balance, testModeSpeaker, updateSettings, testModeMapCanvasRef]);

  useEffect(() => {
    if (!settingsTestModeResult) return;
    const result = settingsTestModeResult.find(res => res.room.id === mapCanvasRoomId);
    drawTestModeMap(result);

    const medianVolume = medianHistoricVolume();
    if (medianVolume && result) {
      const testPoint = {
        roomId: result.room.id,
        positionX: result.positionX,
        positionY: result.positionY,
        volume: medianVolume,
      };
      console.debug(`New test point ${JSON.stringify(testPoint)}`)
      setTestPoints(prevTestPoints => [...prevTestPoints, testPoint]);
      drawTestModeMap(result);
    }
    disableHistoricVolume();
    setReadyToTestLocation(true);
  }, [settingsTestModeResult, mapCanvasRoomId, drawTestModeMap]);

  const measurePoint = useCallback(() => {
    setReadyToTestLocation(false);
    enableHistoricVolume();
  }, []);

  return {
    readyToTestLocation,
    measurePoint,
    errors,
  }
}

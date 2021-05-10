import { RefObject, useCallback, useEffect, useState } from "react";
import { disableHistoricVolume, enableHistoricVolume, medianHistoricVolume } from "./audioMeter";
import { drawCurrentPosition } from "./canvasDrawTools";
import { useSettings } from "./settings";

const testModeMapCanvasSize = 500;

export const useTestMode = (enabled: boolean, testModeMapCanvasRef: RefObject<HTMLCanvasElement> | null = null, mapCanvasRoomId: number | null = null) => {
  const { settingsTestModeResult, updateSettings } = useSettings();

  const [errors, setErrors] = useState<string[]>([]);
  const [readyToTestLocation, setReadyToTestLocation] = useState(false);

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
          await updateSettings({ testMode: true, balance: true });
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
      updateSettings({ testMode: false });
    }
  }, [enabled, updateSettings, testModeMapCanvasRef]);

  useEffect(() => {
    if (!settingsTestModeResult) return;

    const testModeMapContext = testModeMapCanvasRef?.current?.getContext('2d');
    if (testModeMapContext && mapCanvasRoomId) {
      testModeMapContext.clearRect(0, 0, testModeMapCanvasSize, testModeMapCanvasSize);
      const result = settingsTestModeResult.find(res => res.room.id === mapCanvasRoomId);
      if (result) {
        drawCurrentPosition(testModeMapContext, testModeMapCanvasSize, result.positionX, result.positionY)
      }
    }

    const medianVolume = medianHistoricVolume();
    if (medianVolume) {
      console.log(`volume ${medianVolume}`);
    }
    disableHistoricVolume();
    setReadyToTestLocation(true);
  }, [settingsTestModeResult, testModeMapCanvasRef, mapCanvasRoomId]);

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
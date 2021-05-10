import { RefObject, useEffect, useState } from "react";
import { disableHistoricVolume, medianHistoricVolume } from "./audioMeter";
import { drawCurrentPosition } from "./canvasDrawTools";
import { useSettings } from "./settings";

const testModeMapCanvasSize = 500;

export const useTestMode = (enabled: boolean, testModeMapCanvasRef: RefObject<HTMLCanvasElement> | null = null) => {
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
    if (testModeMapContext) {
      testModeMapContext.clearRect(0, 0, testModeMapCanvasSize, testModeMapCanvasSize);
      drawCurrentPosition(testModeMapContext, testModeMapCanvasSize, settingsTestModeResult[0].positionX, settingsTestModeResult[0].positionY)
    }

    const medianVolume = medianHistoricVolume();
    if (medianVolume) {
      console.log(`volume ${medianVolume}`);
    }
    disableHistoricVolume();
  }, [settingsTestModeResult]);

  return {
    readyToTestLocation,
    errors,
  }
}
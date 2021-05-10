import { RefObject, useEffect, useState } from "react";
import { disableHistoricVolume, medianHistoricVolume } from "./audioMeter";
import { useSettings } from "./settings";

export const useTestMode = (enabled: boolean, testModeMapCanvasRef: RefObject<HTMLCanvasElement> | null = null) => {
  const { settingsTestModeResult, updateSettings } = useSettings();

  const [errors, setErrors] = useState<string[]>([]);
  const [readyToTestLocation, setReadyToTestLocation] = useState(false);

  useEffect(() => {
    (async () => {
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
  }, [enabled, updateSettings]);

  useEffect(() => {
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
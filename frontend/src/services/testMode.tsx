import { RefObject, useEffect, useState } from "react";
import { useSettings } from "./settings";

export const useTestMode = (enabled: boolean, testModeMapCanvasRef: RefObject<HTMLCanvasElement> | null = null) => {
    const { settings, updateSettings } = useSettings();

    const [errors, setErrors] = useState<string[]>([]);
    const [readyToTestLocation, setReadyToTestLocation] = useState(false);

    useEffect(() => {
        (async () => {
            try {
                if (enabled) {
                    if (!settings?.balance) {
                        await updateSettings({balance: true});
                    }
                    await updateSettings({testMode: true});
                    setReadyToTestLocation(true);
                } else {
                    await updateSettings({testMode: false});
                }
            } catch(ack) {
                setErrors(prevErr => [...prevErr, ...ack.errors])
            }
        })();

        return () => {
            updateSettings({testMode: false});
        }
    }, [enabled, updateSettings, settings?.balance]);

    return {
        readyToTestLocation,
        errors,
    }
}
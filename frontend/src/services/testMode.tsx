import { useEffect, useState } from "react";
import { useSettings } from "./settings";

export const useTestMode = (enabled: boolean) => {
    const { settings, updateSettings } = useSettings();

    const [errors, setErrors] = useState<string[]>([]);
    const [readyToTestLocation, setReadyToTestLocation] = useState(false);

    useEffect(() => {
        (async () => {
            try {
                await updateSettings({testMode: enabled});
                if (enabled) {
                    if (!settings?.balance) {
                        await updateSettings({balance: true});
                    }

                    setReadyToTestLocation(true);
                }
            } catch(ack) {
                setErrors(prevErr => [...prevErr, ...ack.errors])
            }
        })();
    }, [enabled, updateSettings, settings?.balance])

    return {
        readyToTestLocation,
        errors,
    }
}
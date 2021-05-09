import { useEffect, useState } from "react";
import { useSettings } from "./settings";

export const useTestMode = (enabled: boolean) => {
    const { updateSettings } = useSettings();

    const [errors, setErrors] = useState<string[]>([]);
    const [readyToTestLocation, setReadyToTestLocation] = useState(false);

    useEffect(() => {
        (async () => {
            if (enabled) {
                try {
                    await updateSettings({balance: true});
    
                    setReadyToTestLocation(true);
                } catch(ack) {
                    setErrors(prevErr => [...prevErr, ...ack.errors])
                }
            }
        })();
    }, [enabled])

    return {
        readyToTestLocation,
        errors,
    }
}
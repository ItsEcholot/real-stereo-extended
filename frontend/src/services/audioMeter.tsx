import { useEffect, useState } from 'react';

const targetFrequency = 1000;
const fftWindowSize = 4096;

const AudioContext = window.AudioContext // Default
  || (window as any).webkitAudioContext // Safari and old versions of Chrome;
let audioContext: AudioContext | undefined;

const getMicrophoneStream = async (): Promise<MediaStream> => {
  if (!navigator.mediaDevices) throw new Error(`The browser doesn't support the media devices API, or the context is insecure (is HTTPS being used?)`);
  return await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
}

const stopStream = (stream: MediaStream) => {
  stream.getTracks().forEach(track => track.stop());
}

const getMicrophoneSource = (stream: MediaStream): MediaStreamAudioSourceNode => {
  if (!audioContext) audioContext = new AudioContext();
  return audioContext.createMediaStreamSource(stream);
}

const getAnalyserNode = (fftSize: number): AnalyserNode => {
  if (!audioContext) audioContext = new AudioContext();
  const analyzer = audioContext.createAnalyser();
  analyzer.fftSize = fftSize;
  return analyzer;
}

const closeAudioContext = async () => {
  if (!audioContext) return;
  await audioContext.close();
  audioContext = undefined;
}

// eslint-disable-next-line
const getTotalVolume = (fftData: Uint8Array): number => {
  const sum = fftData.reduce((a, b) => a + b);
  const avg = (sum / fftData.length);
  return 100 * avg / 255;
}

const getFrequencyVolume = (fftData: Uint8Array, lowerFrequencyIndex: number, higherFrequencyIndex: number): number => {
  const avg = (fftData[lowerFrequencyIndex] + fftData[higherFrequencyIndex]) / 2;
  return 100 * avg / 255;
}

export const useAudioMeter = (enabled: boolean) => {
  const [audioMeterErrors, setAudioMeterErrors] = useState<String[]>([]);
  const [volume, setVolume] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setVolume(0);
      setAudioMeterErrors([]);
      return;
    }
    let microphoneStream: MediaStream;
    let analyseInterval: NodeJS.Timeout;
    (async () => {
      try {
        microphoneStream = await getMicrophoneStream();
        const microphoneSource = getMicrophoneSource(microphoneStream);
        const analyserNode = getAnalyserNode(fftWindowSize);
        microphoneSource.connect(analyserNode);

        const bufferData = new Uint8Array(analyserNode.frequencyBinCount);
        if (!audioContext) throw new Error(`Can't get frequency volume: Missing AudioContext`);
        const frequencyPerArrayItem = (audioContext.sampleRate / 2) / analyserNode.frequencyBinCount;
        const lowerFrequencyIndex = Math.floor(targetFrequency / frequencyPerArrayItem)
        const higherFrequencyIndex = lowerFrequencyIndex + 1;

        analyseInterval = setInterval(() => {
          analyserNode.getByteFrequencyData(bufferData);
          //const volume = getTotalVolume(bufferData);
          const volume = getFrequencyVolume(bufferData, lowerFrequencyIndex, higherFrequencyIndex);
          setVolume(volume);
        }, 50);
      } catch (err) {
        setAudioMeterErrors(a => [...a, err.toString()])
      }
    })();

    return () => {
      if (analyseInterval) clearInterval(analyseInterval);
      if (microphoneStream) stopStream(microphoneStream);
      closeAudioContext();
    }
  }, [enabled]);

  return { volume, audioMeterErrors };
};
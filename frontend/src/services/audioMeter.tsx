import { useEffect, useState } from 'react';

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
  //analyzer.fftSize = fftSize;
  return analyzer;
}

const closeAudioContext = async () => {
  if (!audioContext) return;
  await audioContext.close();
  audioContext = undefined;
}

const getVolume = (fftData: Uint8Array) => {
  const sum = fftData.reduce((a, b) => a + b);
  return (sum / fftData.length);
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
        const analyserNode = getAnalyserNode(128);
        microphoneSource.connect(analyserNode);

        const bufferData = new Uint8Array(analyserNode.frequencyBinCount);
        analyseInterval = setInterval(() => {
          analyserNode.getByteFrequencyData(bufferData);
          const volume = getVolume(bufferData);
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
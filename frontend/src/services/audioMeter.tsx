import { useEffect } from 'react';

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

export const useAudioMeter = () => {
  useEffect(() => {

  }, []);
};
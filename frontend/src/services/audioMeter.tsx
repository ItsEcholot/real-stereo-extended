import { RefObject, useEffect, useState } from 'react';
import { drawSpectrumAnalyzer } from './canvasDrawTools';

const fftWindowSize = 512;
const spectrumAnalyzerCanvasWidth = 500;
const spectrumAnalyzerCanvasHeight = 255;
const aWeighting = [
  -85.4,
  -63.6,
  -44.8,
  -30.3,
  -19.1,
  -10.8,
  -4.8,
  0.6,
  1.3,
  0.6,
  -2.5,
  -9.3,
]; // From https://acousticalengineer.com/a-weighting-table/
export let historicVolume: number[] = [];

const AudioContext = window.AudioContext // Default
  || (window as any).webkitAudioContext // Safari and old versions of Chrome;
let audioContext: AudioContext | undefined;

const getMicrophoneStream = async (): Promise<MediaStream> => {
  if (!navigator.mediaDevices) throw new Error(`The browser doesn't support the media devices API, or the context is insecure (is HTTPS being used?)`);
  return await navigator.mediaDevices.getUserMedia({
    audio: {
      autoGainControl: false,
      echoCancellation: false,
      noiseSuppression: false,
    }
  });
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

// sums up energy in bins per octave
const sumEnergy = (fftData: Uint8Array): Uint32Array => {
  // skip the first bin
  let binSize = 1;
  let bin = 0;
  const energies = new Uint32Array(aWeighting.length);
  for (let octave = 0; octave < aWeighting.length; octave++) {
    let sum = 0.0;
    for (let i = 0; i < binSize; i++) {
      sum += fftData[bin++];
    }
    energies[octave] = sum;
    binSize *= 2;
  }

  return energies;
}

const calculateLoudness = (energies: Uint32Array): number => {
  let sum = 0.0;
  for (let i = 0; i < aWeighting.length; i++) {
    sum += energies[i] * Math.pow(10, aWeighting[i] / 10.0);
    energies[i] = energies[i] * Math.pow(10, aWeighting[i] / 10.0);
  }
  return sum / 255;
}

export const prepareAudioMeter = async (): Promise<void> => {
  console.debug('Preparing for calibration by starting & stopping recording');
  const microphoneStream = await getMicrophoneStream();
  if (microphoneStream) stopStream(microphoneStream);
}

export const useAudioMeter = (enabled: boolean, spectrumAnalyzerCanvasRef: RefObject<HTMLCanvasElement> | null = null) => {
  const [audioMeterErrors, setAudioMeterErrors] = useState<String[]>([]);
  const [volume, setVolume] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setVolume(0);
      setAudioMeterErrors([]);
      historicVolume = [];

      const spectrumAnalyzerCanvasContext = spectrumAnalyzerCanvasRef?.current?.getContext('2d');
      if (spectrumAnalyzerCanvasRef && spectrumAnalyzerCanvasRef.current) {
        spectrumAnalyzerCanvasRef.current.width = spectrumAnalyzerCanvasWidth;
        spectrumAnalyzerCanvasRef.current.height = spectrumAnalyzerCanvasHeight;
        if (spectrumAnalyzerCanvasContext) {
          spectrumAnalyzerCanvasContext.clearRect(0, 0, spectrumAnalyzerCanvasWidth, spectrumAnalyzerCanvasHeight);
        }
      }
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
        console.debug('Starting recording');

        const bufferData = new Uint8Array(analyserNode.frequencyBinCount);
        if (!audioContext) throw new Error(`Can't get frequency volume: Missing AudioContext`);
        const frequencyPerArrayItem = (audioContext.sampleRate / 2) / analyserNode.frequencyBinCount;
        /*const lowerFrequencyIndex = Math.floor(targetFrequency / frequencyPerArrayItem)
        const higherFrequencyIndex = lowerFrequencyIndex + 1;*/

        const spectrumAnalyzerCanvasContext = spectrumAnalyzerCanvasRef?.current?.getContext('2d');
        if (spectrumAnalyzerCanvasContext) {
          spectrumAnalyzerCanvasContext.lineWidth = 1;
          spectrumAnalyzerCanvasContext.strokeStyle = '#ff0000';
        }

        analyseInterval = setInterval(() => {
          analyserNode.getByteFrequencyData(bufferData);
          const energies = sumEnergy(bufferData);
          const calcVolume = calculateLoudness(energies);
          setVolume(calcVolume);
          historicVolume.push(calcVolume);

          if (spectrumAnalyzerCanvasContext) {
            spectrumAnalyzerCanvasContext.clearRect(0, 0, spectrumAnalyzerCanvasWidth, spectrumAnalyzerCanvasHeight);
            drawSpectrumAnalyzer(spectrumAnalyzerCanvasContext, bufferData, frequencyPerArrayItem);
          }
        }, 50);
      } catch (err) {
        setAudioMeterErrors(a => [...a, err.toString()]);
      }
    })();

    return () => {
      if (analyseInterval) clearInterval(analyseInterval);
      if (microphoneStream) stopStream(microphoneStream);
      closeAudioContext();
      console.debug('Stopped recording');
    }
  }, [enabled, spectrumAnalyzerCanvasRef]);

  return { volume, audioMeterErrors };
};

import { RefObject, useEffect, useState } from 'react';

const targetFrequency = 1000;
const fftWindowSize = 512;
const lowerFrequencyBoundary = 500;
const higherFrequencyBoundary = 9000;

const AudioContext = window.AudioContext // Default
  || (window as any).webkitAudioContext // Safari and old versions of Chrome;
let audioContext: AudioContext | undefined;

const getMicrophoneStream = async (): Promise<MediaStream> => {
  if (!navigator.mediaDevices) throw new Error(`The browser doesn't support the media devices API, or the context is insecure (is HTTPS being used?)`);
  return await navigator.mediaDevices.getUserMedia({ audio: {
    autoGainControl: false,
    echoCancellation: false,
    noiseSuppression: false,
    mandatory: {
      googEchoCancellation: false,
      googAutoGainControl: false,
      googNoiseSuppression: false,
      googHighpassFilter: false,
    },
  } as any, video: false });
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
const getTotalVolume = (fftData: Uint8Array, frequencyPerArrayItem: number): number => {
  let sum = 0;
  const startIndex = Math.round(lowerFrequencyBoundary / frequencyPerArrayItem);
  const endIndex = Math.round(higherFrequencyBoundary / frequencyPerArrayItem);
  for (let i = startIndex; i < endIndex; i++) {
    if (fftData[i] == -Infinity) console.log('-Infinite sample');
    sum += fftData[i];
  }
  const avg = (sum / (endIndex - startIndex));
  return 100 * avg / 255;
}

const getFrequencyVolume = (fftData: Uint8Array, lowerFrequencyIndex: number, higherFrequencyIndex: number): number => {
  const avg = (fftData[lowerFrequencyIndex] + fftData[higherFrequencyIndex]) / 2;
  return 100 * avg / 255;
}

const drawSpectrumAnalyzer = (context: CanvasRenderingContext2D, fftData: Uint8Array, frequencyPerArrayItem: number) => {
  context.beginPath();
  fftData.forEach((value, index) => {
    context.lineTo(index * 2, value);
    if (index % 25 === 0) {
      context.fillText(`${Math.round(frequencyPerArrayItem * index)}`, index * 2, 250)
    }
  });
  context.stroke();
}

export const useAudioMeter = (enabled: boolean, spectrumAnalyzerCanvasRef: RefObject<HTMLCanvasElement> | null = null) => {
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
        /*const lowerFrequencyIndex = Math.floor(targetFrequency / frequencyPerArrayItem)
        const higherFrequencyIndex = lowerFrequencyIndex + 1;*/

        const spectrumAnalyzerCanvasContext = spectrumAnalyzerCanvasRef?.current?.getContext('2d');
        if (spectrumAnalyzerCanvasContext) {
          spectrumAnalyzerCanvasContext.lineWidth = 1;
          spectrumAnalyzerCanvasContext.strokeStyle = '#ff0000';
        }

        analyseInterval = setInterval(() => {
          analyserNode.getByteFrequencyData(bufferData);

          if (spectrumAnalyzerCanvasContext) {
            spectrumAnalyzerCanvasContext.clearRect(0, 0, spectrumAnalyzerCanvasRef?.current?.width || 0, spectrumAnalyzerCanvasRef?.current?.height || 0);
            drawSpectrumAnalyzer(spectrumAnalyzerCanvasContext, bufferData, frequencyPerArrayItem);
          }

          const volume = getTotalVolume(bufferData, frequencyPerArrayItem);
          //const volume = getFrequencyVolume(bufferData, lowerFrequencyIndex, higherFrequencyIndex);
          setVolume(volume);
        }, 50);
      } catch (err) {
        setAudioMeterErrors(a => [...a, err.toString()]);
      }
    })();

    return () => {
      if (analyseInterval) clearInterval(analyseInterval);
      if (microphoneStream) stopStream(microphoneStream);
      closeAudioContext();
    }
  }, [enabled, spectrumAnalyzerCanvasRef]);

  return { volume, audioMeterErrors };
};
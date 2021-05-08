import { RoomCalibrationPoint } from "./roomCalibration";

export const maxCord = 640;

export const drawSpectrumAnalyzer = (context: CanvasRenderingContext2D, fftData: Uint8Array, frequencyPerArrayItem: number) => {
  context.beginPath();
  fftData.forEach((value, index) => {
    context.lineTo(index * 2, value);
    if ((frequencyPerArrayItem * index) % 1000 === 0) {
      context.fillText(`${Math.round(frequencyPerArrayItem * index)}`, index * 2, 250)
    }
  });
  context.stroke();
}

export const mapCoordinate = (cord: number, canvasSize: number): number => {
  // Remove aliasing using +0.5
  return Math.round((cord / maxCord) * canvasSize) + 0.5;
}

export const getRandomHexColourString = (index: number, saturation: number): string => {
  const maxAmountOfColours = 16;
  const hueDelta = Math.trunc(360 / maxAmountOfColours);
  const h = (index % maxAmountOfColours) * hueDelta;
  let s = saturation;
  let l = 40;

  // convert hsl to rgb from: https://css-tricks.com/converting-color-spaces-in-javascript/
  s /= 100;
  l /= 100;

  let c = (1 - Math.abs(2 * l - 1)) * s,
    x = c * (1 - Math.abs((h / 60) % 2 - 1)),
    m = l - c / 2,
    r = 0,
    g = 0,
    b = 0;

  if (0 <= h && h < 60) {
    r = c; g = x; b = 0;
  } else if (60 <= h && h < 120) {
    r = x; g = c; b = 0;
  } else if (120 <= h && h < 180) {
    r = 0; g = c; b = x;
  } else if (180 <= h && h < 240) {
    r = 0; g = x; b = c;
  } else if (240 <= h && h < 300) {
    r = x; g = 0; b = c;
  } else if (300 <= h && h < 360) {
    r = c; g = 0; b = x;
  }
  // Having obtained RGB, convert channels to hex
  let rString = Math.round((r + m) * 255).toString(16);
  let gString = Math.round((g + m) * 255).toString(16);
  let bString = Math.round((b + m) * 255).toString(16);

  // Prepend 0s, if necessary
  if (rString.length === 1)
    rString = "0" + r;
  if (gString.length === 1)
    gString = "0" + g;
  if (bString.length === 1)
    bString = "0" + b;

  return "#" + rString + gString + bString;
}

export const drawCurrentPosition = (context: CanvasRenderingContext2D, canvasSize: number, x: number, y: number) => {
  const crosshairRadius = 0.03 * canvasSize;
  context.strokeStyle = '#ff0000';
  context.lineWidth = 0.01 * canvasSize;
  context.beginPath();
  context.moveTo(x - crosshairRadius, y);
  context.lineTo(x + crosshairRadius, y);
  context.moveTo(x, y - crosshairRadius);
  context.lineTo(x, y + crosshairRadius);
  context.stroke();
}

export const drawPoints = (context: CanvasRenderingContext2D, canvasSize: number, previousPoints: RoomCalibrationPoint[], fillStyle: string) => {
  const pointRadius = 0.05 * canvasSize;
  context.font = `${0.08 * canvasSize}px sans-serif`;
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.beginPath();
  const points = previousPoints.filter((point, index, arr) => {
    return arr.findIndex(x => (x.coordinateX === point.coordinateX && x.coordinateY === point.coordinateY)) === index
  });

  // draw all points
  points.forEach(point => {
    context.fillStyle = fillStyle;
    context.arc(mapCoordinate(point.coordinateX, canvasSize), mapCoordinate(point.coordinateY, canvasSize), pointRadius, 0, 2 * Math.PI);
    context.fill();
  });

  // draw labels over points
  points.forEach((point, index) => {
    context.fillStyle = '#ffffff';
    context.fillText(`${index+1}`, mapCoordinate(point.coordinateX, canvasSize), mapCoordinate(point.coordinateY, canvasSize));
  });
}

export const drawInterpolation = (context: CanvasRenderingContext2D, canvasSize: number, previousPoints: RoomCalibrationPoint[], colourIndex: number) => {
  const interpolationDebugResolution = canvasSize; // Or anything where canvasSize % interpolationDebugResolution === 0
  const powerParam = 1.5;

  const results = new Array(interpolationDebugResolution);
  let maxResult = 0;

  for (let x = 0; x < interpolationDebugResolution; x++) {
    for (let y = 0; y < interpolationDebugResolution; y++) {
      const mappedX = x * maxCord / interpolationDebugResolution;
      const mappedY = y * maxCord / interpolationDebugResolution;
      let totalWeight = 0;
      let totalVolume = 0;
      let result = 0;
      for (const roomCalibrationPoint of previousPoints) {
        if (roomCalibrationPoint.coordinateX === mappedX && roomCalibrationPoint.coordinateY === mappedY) {
          result = roomCalibrationPoint.measuredVolume;
          break;
        }

        const distanceX = roomCalibrationPoint.coordinateX - mappedX;
        const distanceY = roomCalibrationPoint.coordinateY - mappedY;
        const weight = 1 / Math.pow(Math.sqrt(distanceX**2 + distanceY**2), powerParam)

        totalWeight += weight;
        totalVolume += weight * roomCalibrationPoint.measuredVolume
      }
      if (result === 0) {
        result = totalVolume / totalWeight;
      }

      if (!results[x]) {
        results[x] = new Array(interpolationDebugResolution);
      }
      results[x][y] = result;
      if (result > maxResult) {
        maxResult = result;
      }
    }
  }

  for (let x = 0; x < interpolationDebugResolution; x++) {
    for (let y = 0; y < interpolationDebugResolution; y++) {
      const mappedResult = results[x][y] * 100 / maxResult;
      context.fillStyle = getRandomHexColourString(colourIndex, mappedResult);
      context.fillRect((canvasSize / interpolationDebugResolution) * x, (canvasSize / interpolationDebugResolution) * y, (canvasSize / interpolationDebugResolution), (canvasSize / interpolationDebugResolution));    
    }
  }
}
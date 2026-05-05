import { useCallback, useRef } from 'react';
import type { CaptureFrame } from '../types';

export function useFrameCapture(videoRef: React.RefObject<HTMLVideoElement | null>) {
  const canvasRef = useRef<HTMLCanvasElement>(document.createElement('canvas'));

  const captureFrame = useCallback((): CaptureFrame | null => {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return null;

    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0);
    const imageData = canvas.toDataURL('image/jpeg', 0.85);

    return {
      id: `frame_${Date.now()}`,
      imageData,
      timestamp: Date.now(),
    };
  }, [videoRef]);

  return { captureFrame };
}
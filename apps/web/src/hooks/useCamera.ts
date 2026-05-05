import { useState, useRef, useCallback } from 'react';

export interface CameraState {
  stream: MediaStream | null;
  isActive: boolean;
  error: string | null;
  isRequesting: boolean;
}

export function useCamera() {
  const [state, setState] = useState<CameraState>({
    stream: null,
    isActive: false,
    error: null,
    isRequesting: false,
  });

  const videoRef = useRef<HTMLVideoElement>(null);

  const startCamera = useCallback(async () => {
    setState(prev => ({ ...prev, isRequesting: true, error: null }));
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      setState({ stream, isActive: true, error: null, isRequesting: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al acceder a la cámara';
      setState({ stream: null, isActive: false, error: message, isRequesting: false });
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (state.stream) {
      state.stream.getTracks().forEach(track => track.stop());
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setState({ stream: null, isActive: false, error: null, isRequesting: false });
  }, [state.stream]);

  return { ...state, videoRef, startCamera, stopCamera };
}
import { useEffect } from 'react';
import { useCamera } from '../../hooks/useCamera';

interface CameraPreviewProps {
  onStreamReady?: (stream: MediaStream, videoRef: React.RefObject<HTMLVideoElement | null>) => void;
  onError?: (error: string) => void;
}

export function CameraPreview({ onStreamReady, onError }: CameraPreviewProps) {
  const { videoRef, isActive, isRequesting, error, startCamera, stopCamera, stream } = useCamera();

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  useEffect(() => {
    if (stream && onStreamReady) onStreamReady(stream, videoRef);
  }, [stream]);

  useEffect(() => {
    if (error && onError) onError(error);
  }, [error]);

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '640px' }}>
      {isRequesting && (
        <div style={overlayStyle}>
          <p>Solicitando acceso a la cámara...</p>
        </div>
      )}
      {error && (
        <div style={{ ...overlayStyle, background: 'rgba(200,0,0,0.7)' }}>
          <p>Error: {error}</p>
        </div>
      )}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        style={{
          width: '100%',
          borderRadius: '12px',
          display: isActive ? 'block' : 'none',
          transform: 'scaleX(-1)',
        }}
      />
      {!isActive && !isRequesting && !error && (
        <div style={overlayStyle}>
          <p>Cámara no iniciada</p>
        </div>
      )}
    </div>
  );
}

const overlayStyle: React.CSSProperties = {
  position: 'absolute',
  inset: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'rgba(0,0,0,0.6)',
  color: 'white',
  borderRadius: '12px',
};
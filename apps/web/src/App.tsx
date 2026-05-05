import { useState, useRef } from 'react';
import { HeightInput } from './components/capture-wizard/HeightInput';
import { CameraPreview } from './components/camera-preview/CameraPreview';
import { BodyViewer } from './components/body-viewer/BodyViewer';
import { useCapture } from './hooks/useCapture';

type AppStep = 'height' | 'camera' | 'result';

function App() {
  const [step, setStep] = useState<AppStep>('height');
  const [heightCm, setHeightCm] = useState<number | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const {
    frames, lastResult, calibration, reconstruction,
    bodyMetrics, recommendation, isCapturing, isProcessing,
    startCapturing, resetSession,
  } = useCapture({
    heightCm: heightCm ?? 170,
    videoRef,
  });

  const handleHeightConfirm = (height: number) => {
    setHeightCm(height);
    setStep('camera');
  };

  const handleViewResult = () => setStep('result');

  return (
    <div style={{ minHeight: '100vh', background: '#0f0f0f', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '24px', padding: '24px' }}>
      <h1 style={{ color: 'white', margin: 0, fontSize: '32px', letterSpacing: '4px' }}>BUBA</h1>

      {step === 'height' && <HeightInput onConfirm={handleHeightConfirm} />}

      {step === 'camera' && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', width: '100%', maxWidth: '640px' }}>
          <p style={{ color: '#aaa', margin: 0, fontSize: '14px' }}>
            Altura: <strong style={{ color: 'white' }}>{heightCm} cm</strong>
          </p>

          <CameraPreview
            onStreamReady={(_, ref) => { (videoRef as any).current = ref.current; }}
            onError={(err) => console.error('Error de cámara', err)}
          />

          {lastResult && (
            <div style={{ background: lastResult.accepted ? '#1a3a1a' : '#3a1a1a', border: `1px solid ${lastResult.accepted ? '#4ade80' : '#f87171'}`, borderRadius: '8px', padding: '12px 16px', width: '100%', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'white', fontSize: '14px' }}>Score: <strong>{(lastResult.score * 100).toFixed(0)}%</strong></span>
                <span style={{ color: lastResult.accepted ? '#4ade80' : '#f87171', fontSize: '13px', fontWeight: 600 }}>
                  {lastResult.accepted ? '✓ Aceptado' : '✗ Rechazado'}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '16px', fontSize: '12px' }}>
                <span style={{ color: '#a78bfa' }}>Pose: {lastResult.pose_detected ? `✓ ${lastResult.landmark_count} pts` : '✗'}</span>
                <span style={{ color: '#60a5fa' }}>Orientación: {lastResult.orientation}</span>
                <span style={{ color: lastResult.stability_score >= 0.7 ? '#4ade80' : '#fbbf24' }}>
                  Estabilidad: {(lastResult.stability_score * 100).toFixed(0)}%
                </span>
              </div>
              {lastResult.issues.map(issue => (
                <p key={issue.code} style={{ color: issue.severity === 'error' ? '#f87171' : '#fbbf24', margin: 0, fontSize: '12px' }}>
                  {issue.severity === 'error' ? '✗' : '⚠'} {issue.message}
                </p>
              ))}
            </div>
          )}

          {isProcessing && (
            <div style={{ background: '#2a1a3a', border: '1px solid #a78bfa', borderRadius: '8px', padding: '12px 16px', width: '100%' }}>
              <p style={{ color: '#a78bfa', margin: 0, fontSize: '13px' }}>⏳ Procesando reconstrucción 3D...</p>
            </div>
          )}

          {reconstruction?.success && !isProcessing && (
            <button
              onClick={handleViewResult}
              style={{ background: '#6366f1', color: 'white', border: 'none', borderRadius: '8px', padding: '12px 24px', fontSize: '15px', cursor: 'pointer', fontWeight: 600, width: '100%' }}
            >
              Ver resultado 3D →
            </button>
          )}

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => { const stop = startCapturing(1500); setTimeout(stop, 12000); }}
              disabled={isCapturing || isProcessing}
              style={{ background: isCapturing || isProcessing ? '#444' : '#4f46e5', color: 'white', border: 'none', borderRadius: '8px', padding: '12px 24px', fontSize: '15px', cursor: isCapturing || isProcessing ? 'not-allowed' : 'pointer', fontWeight: 600 }}
            >
              {isCapturing ? 'Capturando...' : isProcessing ? 'Procesando...' : 'Iniciar captura'}
            </button>
            <button
              onClick={() => { resetSession(); setStep('height'); }}
              style={{ background: 'transparent', border: '1px solid #444', color: '#aaa', borderRadius: '8px', padding: '12px 16px', cursor: 'pointer', fontSize: '13px' }}
            >
              Reiniciar
            </button>
          </div>

          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>
            Frames aceptados: <strong style={{ color: 'white' }}>{frames.length}</strong>
          </p>
        </div>
      )}

      {step === 'result' && reconstruction?.joint_positions && (
        <div style={{ width: '100%', maxWidth: '720px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <BodyViewer
            vertices={reconstruction.vertices ?? []}
            faces={reconstruction.faces ?? []}
            jointPositions={reconstruction.joint_positions}
          />

          {bodyMetrics && (
            <div style={{ background: '#1a1a2a', border: '1px solid #818cf8', borderRadius: '8px', padding: '12px 16px' }}>
              <p style={{ color: '#818cf8', margin: '0 0 6px 0', fontSize: '13px', fontWeight: 600 }}>
                Medidas 3D — Tipo: {bodyMetrics.body_type}
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', fontSize: '12px' }}>
                {Object.entries(bodyMetrics.measurements).map(([key, val]) => (
                  <span key={key} style={{ color: '#aaa' }}>
                    {key.replace(/_/g, ' ')}: <strong style={{ color: 'white' }}>{val} cm</strong>
                  </span>
                ))}
              </div>
            </div>
          )}

          {recommendation && (
            <div style={{ background: '#1a2a2a', border: '1px solid #2dd4bf', borderRadius: '8px', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <p style={{ color: '#2dd4bf', margin: 0, fontSize: '13px', fontWeight: 600 }}>Recomendaciones</p>
              <p style={{ color: '#aaa', margin: 0, fontSize: '12px' }}>{recommendation.description}</p>
              <div style={{ display: 'flex', gap: '12px', fontSize: '12px' }}>
                {recommendation.size_estimate.top && <span style={{ color: '#aaa' }}>Top: <strong style={{ color: 'white' }}>{recommendation.size_estimate.top}</strong></span>}
                {recommendation.size_estimate.bottom && <span style={{ color: '#aaa' }}>Bottom: <strong style={{ color: 'white' }}>{recommendation.size_estimate.bottom}</strong></span>}
              </div>
              <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {recommendation.recommendations.tops.map(t => (
                  <span key={t} style={{ color: '#aaa' }}>▸ {t}</span>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => { resetSession(); setStep('height'); }}
            style={{ background: 'transparent', border: '1px solid #444', color: '#aaa', borderRadius: '8px', padding: '12px 16px', cursor: 'pointer', fontSize: '13px' }}
          >
            Nueva captura
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
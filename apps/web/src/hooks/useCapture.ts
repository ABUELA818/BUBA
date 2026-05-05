import { useState, useCallback, useRef } from 'react';
import type { CaptureFrame, QualityResult } from '../types';
import { api } from '../services/api';
import type { CalibrationResult, ReconstructionResult, MetricsResult, RecommendationResult } from '../services/api';

interface UseCaptureProps {
  heightCm: number;
  videoRef: React.RefObject<HTMLVideoElement | null>;
}

const FRAMES_FOR_CALIBRATION = 3;

export function useCapture({ heightCm, videoRef }: UseCaptureProps) {
  const [frames, setFrames] = useState<CaptureFrame[]>([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [lastResult, setLastResult] = useState<QualityResult | null>(null);
  const [calibration, setCalibration] = useState<CalibrationResult | null>(null);
  const [reconstruction, setReconstruction] = useState<ReconstructionResult | null>(null);
  const [bodyMetrics, setBodyMetrics] = useState<MetricsResult | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const sessionIdRef = useRef<string | null>(null);
  const landmarkBufferRef = useRef<any[]>([]);
  const calibratedRef = useRef(false);
  const reconstructedRef = useRef(false);

  const ensureSession = useCallback(async () => {
    if (sessionIdRef.current) return sessionIdRef.current;
    const { session_id } = await api.createSession(heightCm);
    sessionIdRef.current = session_id;
    return session_id;
  }, [heightCm]);

  const runFullPipeline = useCallback(async (landmarks: any[]) => {
    if (reconstructedRef.current) return;
    reconstructedRef.current = true;
    setIsProcessing(true);

    try {
      const recon = await api.reconstruct(landmarks, heightCm);
      setReconstruction(recon);

      if (recon.success && recon.joint_positions && recon.scale) {
        const met = await api.computeMetrics(recon.joint_positions, recon.scale);
        setBodyMetrics(met);

        const rec = await api.getRecommendation(met.body_type, met.measurements);
        setRecommendation(rec);
      }
    } catch (err) {
      console.error('Error en pipeline completo', err);
      reconstructedRef.current = false;
    } finally {
      setIsProcessing(false);
    }
  }, [heightCm]);

  const captureAndAnalyze = useCallback(async () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0);
    const imageData = canvas.toDataURL('image/jpeg', 0.85);

    const frame: CaptureFrame = {
      id: `frame_${Date.now()}`,
      imageData,
      timestamp: Date.now(),
    };

    try {
      const result = await api.analyzeFrame(imageData, heightCm);
      frame.qualityScore = result.score;
      frame.accepted = result.accepted;
      setLastResult(result);

      if (result.accepted) {
        setFrames(prev => [...prev, frame]);

        if (result.landmarks.length > 0) {
          landmarkBufferRef.current.push(result.landmarks);
        }

        const sessionId = await ensureSession();
        await api.addFrame(
          sessionId,
          result.score,
          result.orientation,
          result.stability_score,
          result.landmark_count,
        );

        if (!calibratedRef.current && landmarkBufferRef.current.length >= FRAMES_FOR_CALIBRATION) {
          calibratedRef.current = true;
          const midLandmarks = landmarkBufferRef.current[Math.floor(landmarkBufferRef.current.length / 2)];
          const cal = await api.calibrate(midLandmarks, heightCm);
          setCalibration(cal);
        }

        if (landmarkBufferRef.current.length >= 5 && !reconstructedRef.current) {
          const midLandmarks = landmarkBufferRef.current[Math.floor(landmarkBufferRef.current.length / 2)];
          await runFullPipeline(midLandmarks);
        }
      }
    } catch (err) {
      console.error('Error analizando frame', err);
    }
  }, [heightCm, videoRef, ensureSession, runFullPipeline]);

  const startCapturing = useCallback((intervalMs = 1500) => {
    setIsCapturing(true);
    const id = setInterval(captureAndAnalyze, intervalMs);
    const stop = () => {
      clearInterval(id);
      setIsCapturing(false);
    };
    return stop;
  }, [captureAndAnalyze]);

  const resetSession = useCallback(() => {
    sessionIdRef.current = null;
    landmarkBufferRef.current = [];
    calibratedRef.current = false;
    reconstructedRef.current = false;
    setFrames([]);
    setLastResult(null);
    setCalibration(null);
    setReconstruction(null);
    setBodyMetrics(null);
    setRecommendation(null);
    setIsProcessing(false);
  }, []);

  return {
    frames,
    isCapturing,
    isProcessing,
    lastResult,
    calibration,
    reconstruction,
    bodyMetrics,
    recommendation,
    startCapturing,
    resetSession,
  };
}
import axios from 'axios';
import type { QualityResult, LandmarkPoint } from '../types';

const client = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
});

export interface CalibrationResult {
  success: boolean;
  scale_factor: number | null;
  segments: {
    shoulder_width?: number;
    hip_width?: number;
    torso_length?: number;
    leg_length?: number;
  };
  message: string;
}

export interface ReconstructionResult {
  success: boolean;
  message: string;
  betas?: number[];
  scale?: number;
  joint_positions?: number[][];
  vertices?: number[][];
  faces?: number[][];
  vt?: number[][];
  ft?: number[][];
}

export interface MetricsResult {
  measurements: {
    shoulder_width?: number;
    hip_width?: number;
    torso_length?: number;
    left_leg?: number;
    right_leg?: number;
    avg_leg_length?: number;
  };
  body_type: string;
  confidence: string;
}

export interface RecommendationResult {
  body_type: string;
  description: string;
  recommendations: {
    tops: string[];
    bottoms: string[];
    avoid: string[];
  };
  size_estimate: {
    top?: string;
    bottom?: string;
  };
}

export const api = {
  health: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  createSession: async (heightCm: number): Promise<{ session_id: string }> => {
    const res = await client.post('/sessions', { height_cm: heightCm });
    return res.data;
  },

  addFrame: async (
    sessionId: string,
    qualityScore: number,
    orientation: string,
    stabilityScore: number,
    landmarkCount: number,
  ): Promise<void> => {
    await client.post(`/sessions/${sessionId}/frames`, {
      session_id: sessionId,
      quality_score: qualityScore,
      orientation,
      stability_score: stabilityScore,
      landmark_count: landmarkCount,
    });
  },

  analyzeFrame: async (imageData: string, heightCm: number): Promise<QualityResult> => {
    const res = await client.post('/capture/analyze', {
      image_data: imageData,
      height_cm: heightCm,
    });
    return res.data;
  },

  calibrate: async (landmarks: LandmarkPoint[], heightCm: number): Promise<CalibrationResult> => {
    const res = await client.post('/calibration/compute', {
      landmarks,
      height_cm: heightCm,
    });
    return res.data;
  },

  reconstruct: async (landmarks: LandmarkPoint[], heightCm: number): Promise<ReconstructionResult> => {
    const res = await client.post('/reconstruction/compute', {
      landmarks,
      height_cm: heightCm,
    });
    return res.data;
  },

  computeMetrics: async (jointPositions: number[][], scale: number): Promise<MetricsResult> => {
    const res = await client.post('/metrics/compute', {
      joint_positions: jointPositions,
      scale,
    });
    return res.data;
  },

  getRecommendation: async (bodyType: string, measurements: object): Promise<RecommendationResult> => {
    const res = await client.post('/recommendation/compute', {
      body_type: bodyType,
      measurements,
    });
    return res.data;
  },

  analyzeFace: async (imageData: string): Promise<FaceResult> => {
    const res = await client.post('/face/analyze', {
      image_data: imageData,
    });
    return res.data;
  },

  extractTexture: async (imageData: string): Promise<TextureResult> => {
    const res = await client.post('/texture/extract', {
      image_data: imageData,
    });
    return res.data;
  },
};

export interface FaceResult {
  detected: boolean;
  landmarks: LandmarkPoint[];
  blendshapes: Record<string, number>;
  face_metrics: {
    face_ratio?: number;
    eye_spacing_ratio?: number;
    mouth_width_ratio?: number;
    face_shape?: string;
  };
  landmark_count: number;
}

export interface TextureResult {
  success: boolean;
  face_texture: string | null;
  hair_color: string | null;
  hair_style: string | null;
  message: string;
}
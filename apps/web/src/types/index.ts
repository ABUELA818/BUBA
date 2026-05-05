export interface UserSession {
  id: string;
  heightCm: number;
  createdAt: Date;
}

export interface CaptureFrame {
  id: string;
  imageData: string;
  timestamp: number;
  qualityScore?: number;
  accepted?: boolean;
}

export interface QualityIssue {
  code: string;
  message: string;
  severity: 'warning' | 'error';
}

export interface LandmarkPoint {
  x: number;
  y: number;
  z: number;
}

export interface QualityResult {
  score: number;
  accepted: boolean;
  issues: QualityIssue[];
  orientation: 'front' | 'profile' | 'back' | 'unknown';
  pose_detected: boolean;
  landmarks: LandmarkPoint[];
  landmark_count: number;
  stability_score: number;
}

export interface CaptureState {
  status: 'idle' | 'requesting' | 'previewing' | 'capturing' | 'processing' | 'done' | 'error';
  heightCm: number | null;
  frames: CaptureFrame[];
  error: string | null;
}
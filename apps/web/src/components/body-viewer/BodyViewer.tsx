import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Environment } from '@react-three/drei';
import { useMemo } from 'react';
import * as THREE from 'three';

interface BodyViewerProps {
  vertices: number[][];
  faces: number[][];
  jointPositions: number[][];
}

function BodyMesh({ vertices, faces }: { vertices: number[][], faces: number[][] }) {
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();

    const positions = new Float32Array(vertices.flatMap(v => [v[0], v[1], v[2]]));
    const indices = new Uint32Array(faces.flatMap(f => [f[0], f[1], f[2]]));

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setIndex(new THREE.BufferAttribute(indices, 1));
    geo.computeVertexNormals();

    return geo;
  }, [vertices, faces]);

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        color="#c8a882"
        roughness={0.7}
        metalness={0.0}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function JointSkeleton({ joints }: { joints: number[][] }) {
  const CONNECTIONS = [
    [1, 2], [1, 4], [2, 5], [4, 7], [5, 8],
    [1, 16], [2, 17], [16, 18], [17, 19],
    [18, 20], [19, 21], [0, 12], [12, 15],
  ];

  const lines = useMemo(() => {
    return CONNECTIONS.map(([a, b]) => {
      if (a >= joints.length || b >= joints.length) return null;
      const points = [
        new THREE.Vector3(joints[a][0], joints[a][1], joints[a][2]),
        new THREE.Vector3(joints[b][0], joints[b][1], joints[b][2]),
      ];
      return new THREE.BufferGeometry().setFromPoints(points);
    }).filter(Boolean);
  }, [joints]);

  return (
    <>
      {lines.map((geo, i) => (
        <line key={i}>
          <primitive object={geo} attach="geometry" />
          <lineBasicMaterial color="#6366f1" linewidth={2} />
        </line>
      ))}
      {joints.map((j, i) => (
        <mesh key={i} position={[j[0], j[1], j[2]]}>
          <sphereGeometry args={[0.012, 8, 8]} />
          <meshStandardMaterial color="#a78bfa" />
        </mesh>
      ))}
    </>
  );
}

export function BodyViewer({ vertices, faces, jointPositions }: BodyViewerProps) {
  const center = useMemo(() => {
    if (!jointPositions.length) return [0, 0, 0];
    const avg = jointPositions.reduce((a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], [0, 0, 0]);
    return avg.map(v => v / jointPositions.length);
  }, [jointPositions]);

  const hasMesh = vertices.length > 0 && faces.length > 0;

  return (
    <div style={{ width: '100%', height: '500px', borderRadius: '12px', overflow: 'hidden', background: '#111' }}>
      <Canvas camera={{ position: [0, 0, 3], fov: 50 }} style={{ background: '#111' }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 4, 2]} intensity={1.2} />
        <directionalLight position={[-2, 2, -2]} intensity={0.4} />
        <Environment preset="city" />

        <group position={[-center[0], -center[1], -center[2]]}>
          {hasMesh && <BodyMesh vertices={vertices} faces={faces} />}
          {jointPositions.length > 0 && <JointSkeleton joints={jointPositions} />}
        </group>

        <Grid args={[4, 4]} position={[0, -1, 0]} cellColor="#333" sectionColor="#444" />
        <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} autoRotate={true} autoRotateSpeed={1} />
      </Canvas>
    </div>
  );
}
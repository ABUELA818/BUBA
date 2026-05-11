import { useMemo } from 'react';
import * as THREE from 'three';

export type HairStyle = 'short' | 'medium' | 'long' | 'curly' | 'bald';

interface HairMeshProps {
  headPosition: [number, number, number];
  hairStyle: HairStyle;
  hairColor: string;
}

function createShortHair(head: THREE.Vector3): THREE.BufferGeometry {
  const geo = new THREE.SphereGeometry(0.13, 16, 16, 0, Math.PI * 2, 0, Math.PI * 0.5);
  geo.translate(head.x, head.y + 0.06, head.z);
  return geo;
}

function createMediumHair(head: THREE.Vector3): THREE.BufferGeometry {
  const top = new THREE.SphereGeometry(0.13, 16, 16, 0, Math.PI * 2, 0, Math.PI * 0.55);
  top.translate(0, 0.06, 0);

  const side = new THREE.CylinderGeometry(0.12, 0.1, 0.15, 16);
  side.translate(0, -0.08, 0);

  const merged = mergeGeometries([top, side]);
  merged.translate(head.x, head.y, head.z);
  return merged;
}

function createLongHair(head: THREE.Vector3): THREE.BufferGeometry {
  const top = new THREE.SphereGeometry(0.13, 16, 16, 0, Math.PI * 2, 0, Math.PI * 0.55);
  top.translate(0, 0.06, 0);

  const body = new THREE.CylinderGeometry(0.11, 0.08, 0.35, 16);
  body.translate(0, -0.18, 0);

  const merged = mergeGeometries([top, body]);
  merged.translate(head.x, head.y, head.z);
  return merged;
}

function createCurlyHair(head: THREE.Vector3): THREE.BufferGeometry {
  const base = new THREE.SphereGeometry(0.16, 16, 16, 0, Math.PI * 2, 0, Math.PI * 0.6);
  base.translate(head.x, head.y + 0.08, head.z);
  return base;
}

function mergeGeometries(geos: THREE.BufferGeometry[]): THREE.BufferGeometry {
  const positions: number[] = [];
  const normals: number[] = [];

  for (const geo of geos) {
    const pos = geo.attributes.position.array;
    const nor = geo.attributes.normal?.array;
    for (let i = 0; i < pos.length; i++) positions.push(pos[i]);
    if (nor) for (let i = 0; i < nor.length; i++) normals.push(nor[i]);
  }

  const merged = new THREE.BufferGeometry();
  merged.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  if (normals.length > 0) {
    merged.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  } else {
    merged.computeVertexNormals();
  }
  return merged;
}

export function HairMesh({ headPosition, hairStyle, hairColor }: HairMeshProps) {
  const geometry = useMemo(() => {
    const head = new THREE.Vector3(...headPosition);
    switch (hairStyle) {
      case 'short': return createShortHair(head);
      case 'medium': return createMediumHair(head);
      case 'long': return createLongHair(head);
      case 'curly': return createCurlyHair(head);
      case 'bald': return null;
      default: return createShortHair(head);
    }
  }, [headPosition, hairStyle]);

  if (!geometry) return null;

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        color={hairColor}
        roughness={0.9}
        metalness={0.0}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}
import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, Float } from '@react-three/drei';
import * as THREE from 'three';

function OrbMesh() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.002;
      meshRef.current.rotation.y += 0.004;
      meshRef.current.position.y = Math.sin(clock.elapsedTime * 0.5) * 0.15;
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.5}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.2, 64, 64]} />
        <meshStandardMaterial 
          color="#1C2E1E"
          roughness={0.15}
          metalness={0.8}
          envMapIntensity={0.5}
        />
      </mesh>
    </Float>
  );
}

export default function FloatingOrb() {
  return (
    <div className="absolute right-[10%] lg:right-1/4 top-1/2 -translate-y-1/2 w-64 h-64 opacity-20 lg:opacity-30 pointer-events-none z-[1] hidden md:block">
      <Canvas 
        camera={{ position: [0, 0, 5], fov: 45 }} 
        dpr={[1, 2]} 
        style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[2, 4, 3]} intensity={1} />
        <OrbMesh />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}

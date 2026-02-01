"use client"
import React, { useRef, useMemo, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame, ThreeEvent } from '@react-three/fiber';
import { Stars } from '@react-three/drei';
import * as THREE from 'three';

interface InteractiveProps {
  position: [number, number, number];
  color: string;
  speed: number;
}

function useHighlightOnHover() {
  const [hovered, setHovered] = useState(false);
  const bind = useMemo(() => ({
    onPointerOver: () => setHovered(true),
    onPointerOut: () => setHovered(false),
  }), []);
  return { hovered, bind };
}

function useDragRotate(meshRef: React.RefObject<THREE.Mesh | null>) {
  const isDragging = useRef(false);
  const lastX = useRef(0);
  const lastY = useRef(0);

  const bind = useMemo(() => ({
    onPointerDown: (e: ThreeEvent<PointerEvent>) => {
      isDragging.current = true;
      lastX.current = e.clientX;
      lastY.current = e.clientY;
    },
    onPointerMove: (e: ThreeEvent<PointerEvent>) => {
      if (!isDragging.current || !meshRef.current) return;
      const x = e.clientX;
      const y = e.clientY;
      const dx = (x - lastX.current) * 0.01;
      const dy = (y - lastY.current) * 0.01;
      meshRef.current.rotation.y += dx;
      meshRef.current.rotation.x += dy;
      lastX.current = x;
      lastY.current = y;
    },
    onPointerUp: () => {
      isDragging.current = false;
    },
  }), [meshRef]);

  return bind;
}

function FloatingCube({ position, color, speed }: InteractiveProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const { hovered, bind: hoverBind } = useHighlightOnHover();
  const dragBind = useDragRotate(meshRef);

  useFrame((state) => {
    if (meshRef.current && !hovered) {
      meshRef.current.rotation.x += speed * 0.003;
      meshRef.current.rotation.y += speed * 0.003;
      meshRef.current.position.y += Math.sin(state.clock.elapsedTime * speed * 0.5) * 0.02;
      meshRef.current.position.x += Math.cos(state.clock.elapsedTime * speed * 0.25) * 0.01;
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      castShadow
      receiveShadow
      {...hoverBind}
      {...dragBind}
      onPointerLeave={hoverBind.onPointerOut} // Extra safety
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshPhysicalMaterial
        color={color}
        transparent
        opacity={hovered ? 1 : 0.85}
        metalness={0.5}
        roughness={0.15}
        clearcoat={0.6}
        sheen={0.5}
        emissive={hovered ? color : '#000'}
        emissiveIntensity={hovered ? 0.25 : 0}
      />
    </mesh>
  );
}

function FloatingSphere({ position, color, speed }: InteractiveProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const { hovered, bind: hoverBind } = useHighlightOnHover();
  const dragBind = useDragRotate(meshRef);

  useFrame((state) => {
    if (meshRef.current && !hovered) {
      meshRef.current.rotation.x += speed * 0.0015;
      meshRef.current.rotation.z += speed * 0.0015;
      meshRef.current.position.x += Math.sin(state.clock.elapsedTime * speed * 0.5) * 0.015;
      meshRef.current.position.z += Math.cos(state.clock.elapsedTime * speed * 0.35) * 0.01;
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      castShadow
      receiveShadow
      {...hoverBind}
      {...dragBind}
      onPointerLeave={hoverBind.onPointerOut} // Extra safety
    >
      <sphereGeometry args={[0.6, 48, 48]} />
      <meshPhysicalMaterial
        color={color}
        transparent
        opacity={hovered ? 0.95 : 0.7}
        metalness={0.6}
        roughness={0.08}
        clearcoat={0.7}
        sheen={0.7}
        emissive={hovered ? color : '#000'}
        emissiveIntensity={hovered ? 0.18 : 0}
      />
    </mesh>
  );
}

function FloatingTorus({ position, color, speed }: InteractiveProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const { hovered, bind: hoverBind } = useHighlightOnHover();
  const dragBind = useDragRotate(meshRef);

  useFrame((state) => {
    if (meshRef.current && !hovered) {
      meshRef.current.rotation.x += speed * 0.0025;
      meshRef.current.rotation.y += speed * 0.0025;
      meshRef.current.position.y += Math.cos(state.clock.elapsedTime * speed * 0.5) * 0.02;
      meshRef.current.position.z += Math.sin(state.clock.elapsedTime * speed * 0.25) * 0.01;
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      castShadow
      receiveShadow
      {...hoverBind}
      {...dragBind}
      onPointerLeave={hoverBind.onPointerOut} // Extra safety
    >
      <torusGeometry args={[0.5, 0.2, 24, 100]} />
      <meshPhysicalMaterial
        color={color}
        transparent
        opacity={hovered ? 0.8 : 0.65}
        metalness={0.45}
        roughness={0.18}
        clearcoat={0.5}
        sheen={0.5}
        emissive={hovered ? color : '#000'}
        emissiveIntensity={hovered ? 0.15 : 0}
      />
    </mesh>
  );
}

function generateFloatingElements(count: number) {
  const elements = [];
  const colors = ['#8B5CF6', '#F59E42', '#38BDF8', '#F472B6', '#34D399', '#FBBF24'];
  for (let i = 0; i < count; i++) {
    const type = i % 3;
    const position: [number, number, number] = [
      (Math.random() - 0.5) * 7,
      (Math.random() - 0.5) * 5,
      (Math.random() - 0.5) * 5
    ];
    const color = colors[Math.floor(Math.random() * colors.length)];
    const speed = 0.5 + Math.random() * 1.2;
    if (type === 0) {
      elements.push(<FloatingCube key={`cube-${i}`} position={position} color={color} speed={speed} />);
    } else if (type === 1) {
      elements.push(<FloatingSphere key={`sphere-${i}`} position={position} color={color} speed={speed} />);
    } else {
      elements.push(<FloatingTorus key={`torus-${i}`} position={position} color={color} speed={speed} />);
    }
  }
  return elements;
}

// Standalone WebGL check function
function isWebGLAvailable() {
  if (typeof window === 'undefined') return false;
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (
      canvas.getContext('webgl2') || canvas.getContext('webgl')
    ));
  } catch {
    return false;
  }
}

export default function ThreeJSBackground() {
  const [isSceneReady, setIsSceneReady] = useState(false);
  const [elementCount, setElementCount] = useState(10);
  const [dpr, setDpr] = useState(2);

  const elements = useMemo(() => generateFloatingElements(elementCount), [elementCount]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (window.innerWidth < 768) {
        setElementCount(5);
        setDpr(1);
      }
    }
  }, []);

  const webGLAvailable = useMemo(() => isWebGLAvailable(), []);

  if (typeof window !== 'undefined' && !webGLAvailable) {
    return (
      <div className="fixed inset-0 -z-10 bg-black">
        <div className="absolute inset-0 flex items-center justify-center text-gray-500 text-sm">
          3D background unavailable
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-0 pointer-events-none bg-black">
      {/* Neutral Fallback Layer */}
      {!isSceneReady && (
        <div className="absolute inset-0 z-0 flex items-center justify-center">
          <div className="w-12 h-12 rounded-full border-2 border-white/5 border-t-white/20 animate-spin" />
        </div>
      )}

      <div
        className="absolute inset-0 transition-opacity duration-1000 ease-in-out"
        style={{ opacity: isSceneReady ? 1 : 0 }}
      >
        <Suspense fallback={null}>
          <Canvas
            camera={{ position: [0, 0, 7], fov: 55 }}
            style={{
              background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)', // Neutral dark theme
              position: 'absolute',
              inset: 0
            }}
            dpr={dpr}
            onCreated={() => {
              // Ensure objects are rendered before showing
              setTimeout(() => setIsSceneReady(true), 100);
            }}
            shadows
          >
            <ambientLight intensity={0.85} />
            <directionalLight
              position={[5, 10, 7]}
              intensity={1.3}
              color="#fff"
              castShadow
              shadow-mapSize-width={1024}
              shadow-mapSize-height={1024}
            />
            <Stars radius={30} depth={40} count={600} factor={4} saturation={0.8} fade speed={1} />
            {elements}
          </Canvas>
        </Suspense>
      </div>
    </div>
  );
}
"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

interface ThreeAiCoreProps {
  className?: string;
}

export const ThreeAiCore: React.FC<ThreeAiCoreProps> = ({ className = "" }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [webGlSupported, setWebGlSupported] = useState<boolean>(true);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // 1. Detect WebGL support
    const checkWebGL = () => {
      try {
        const testCanvas = document.createElement("canvas");
        return !!(
          window.WebGLRenderingContext &&
          (testCanvas.getContext("webgl") || testCanvas.getContext("experimental-webgl"))
        );
      } catch {
        return false;
      }
    };

    if (!checkWebGL()) {
      setWebGlSupported(false);
      return;
    }

    // 2. Check prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // 3. Setup Three.js Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const width = container.clientWidth || 500;
    const height = container.clientHeight || 500;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 7;

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;

    container.appendChild(renderer.domElement);

    // 4. Lighting (Vignan Navy & Tech Indigo/Cyan)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const blueLight = new THREE.PointLight(0x2563eb, 3.5, 50);
    blueLight.position.set(4, 5, 4);
    scene.add(blueLight);

    const cyanLight = new THREE.PointLight(0x06b6d4, 2.5, 50);
    cyanLight.position.set(-4, -3, 3);
    scene.add(cyanLight);

    const purpleLight = new THREE.PointLight(0x6366f1, 2.0, 50);
    purpleLight.position.set(0, -4, -3);
    scene.add(purpleLight);

    // 5. Hierarchy Root Group
    const coreGroup = new THREE.Group();
    scene.add(coreGroup);

    // 6. Central Glowing Core Sphere
    const coreGeometry = new THREE.SphereGeometry(1.2, 32, 32);
    const coreMaterial = new THREE.MeshStandardMaterial({
      color: 0x1d4ed8,
      emissive: 0x1e40af,
      emissiveIntensity: 0.6,
      roughness: 0.15,
      metalness: 0.85,
      wireframe: false,
    });
    const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
    coreGroup.add(coreMesh);

    // Subtle Core Wireframe Shell
    const shellGeometry = new THREE.IcosahedronGeometry(1.35, 2);
    const shellMaterial = new THREE.MeshBasicMaterial({
      color: 0x60a5fa,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const shellMesh = new THREE.Mesh(shellGeometry, shellMaterial);
    coreGroup.add(shellMesh);

    // 7. Floating Orbital Rings (3 Torus rings with independent tilts)
    const ring1Geo = new THREE.TorusGeometry(1.85, 0.022, 16, 100);
    const ring1Mat = new THREE.MeshStandardMaterial({
      color: 0x3b82f6,
      emissive: 0x2563eb,
      emissiveIntensity: 0.4,
      metalness: 0.9,
      roughness: 0.2,
    });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1.rotation.x = Math.PI / 3;
    ring1.rotation.y = Math.PI / 6;
    coreGroup.add(ring1);

    const ring2Geo = new THREE.TorusGeometry(2.25, 0.018, 16, 100);
    const ring2Mat = new THREE.MeshStandardMaterial({
      color: 0x06b6d4,
      emissive: 0x0891b2,
      emissiveIntensity: 0.4,
      metalness: 0.9,
      roughness: 0.2,
    });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = -Math.PI / 4;
    ring2.rotation.y = Math.PI / 4;
    coreGroup.add(ring2);

    const ring3Geo = new THREE.TorusGeometry(2.6, 0.015, 16, 100);
    const ring3Mat = new THREE.MeshStandardMaterial({
      color: 0x818cf8,
      emissive: 0x6366f1,
      emissiveIntensity: 0.3,
      metalness: 0.8,
      roughness: 0.3,
    });
    const ring3 = new THREE.Mesh(ring3Geo, ring3Mat);
    ring3.rotation.x = Math.PI / 2.2;
    ring3.rotation.z = Math.PI / 5;
    coreGroup.add(ring3);

    // 8. Particle Swarm & Neural Nodes
    const particleCount = 280;
    const positions = new Float32Array(particleCount * 3);
    const particleColors = new Float32Array(particleCount * 3);

    const pColor1 = new THREE.Color(0x38bdf8);
    const pColor2 = new THREE.Color(0x818cf8);
    const pColor3 = new THREE.Color(0x60a5fa);

    for (let i = 0; i < particleCount; i++) {
      // Golden ratio spherical distribution
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;
      const radius = 2.1 + Math.random() * 1.4;

      positions[i * 3] = radius * Math.cos(theta) * Math.sin(phi);
      positions[i * 3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      const chosenColor = i % 3 === 0 ? pColor1 : i % 3 === 1 ? pColor2 : pColor3;
      particleColors[i * 3] = chosenColor.r;
      particleColors[i * 3 + 1] = chosenColor.g;
      particleColors[i * 3 + 2] = chosenColor.b;
    }

    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    particleGeometry.setAttribute("color", new THREE.BufferAttribute(particleColors, 3));

    const particleMaterial = new THREE.PointsMaterial({
      size: 0.055,
      vertexColors: true,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending,
    });

    const particleSystem = new THREE.Points(particleGeometry, particleMaterial);
    coreGroup.add(particleSystem);

    // 9. Interactive Mouse Parallax (Damped / Smoothed)
    let targetMouseX = 0;
    let targetMouseY = 0;
    let currentMouseX = 0;
    let currentMouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      targetMouseX = x * 0.8;
      targetMouseY = y * 0.8;
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });

    // 10. Visibility Optimization (Pause rendering when off-screen)
    let isVisible = true;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          isVisible = entry.isIntersecting;
        });
      },
      { threshold: 0.05 }
    );
    observer.observe(container);

    // 11. Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      if (!isVisible) return;

      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      // Lerp mouse interaction
      currentMouseX += (targetMouseX - currentMouseX) * 0.05;
      currentMouseY += (targetMouseY - currentMouseY) * 0.05;

      if (!prefersReducedMotion) {
        // Core rotation
        coreMesh.rotation.y += delta * 0.35;
        shellMesh.rotation.y -= delta * 0.25;
        shellMesh.rotation.x += delta * 0.15;

        // Orbital ring rotations
        ring1.rotation.z += delta * 0.45;
        ring2.rotation.y += delta * 0.35;
        ring3.rotation.x -= delta * 0.3;

        // Particle swarm rotation
        particleSystem.rotation.y += delta * 0.12;
        particleSystem.rotation.z += delta * 0.08;

        // Gentle floating oscillation
        coreGroup.position.y = Math.sin(elapsedTime * 1.4) * 0.08;

        // Mouse Parallax tilt
        coreGroup.rotation.y = currentMouseX * 0.8;
        coreGroup.rotation.x = currentMouseY * 0.8;
      } else {
        // Minimal static presentation for reduced motion
        coreGroup.rotation.y = currentMouseX * 0.2;
        coreGroup.rotation.x = currentMouseY * 0.2;
      }

      renderer.render(scene, camera);
    };

    animate();

    // 12. Handle Resizing
    const handleResize = () => {
      if (!container) return;
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      if (newWidth === 0 || newHeight === 0) return;

      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    // 13. Resource Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      observer.disconnect();
      resizeObserver.disconnect();
      window.removeEventListener("mousemove", handleMouseMove);

      if (renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }

      // Dispose Geometries & Materials
      coreGeometry.dispose();
      coreMaterial.dispose();
      shellGeometry.dispose();
      shellMaterial.dispose();
      ring1Geo.dispose();
      ring1Mat.dispose();
      ring2Geo.dispose();
      ring2Mat.dispose();
      ring3Geo.dispose();
      ring3Mat.dispose();
      particleGeometry.dispose();
      particleMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  if (!webGlSupported) {
    // Graceful CSS Fallback when WebGL is unavailable
    return (
      <div className={`relative flex items-center justify-center ${className}`}>
        <div className="relative w-72 h-72 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-2 border-dashed border-blue-400/40 animate-[spin_20s_linear_infinite]" />
          <div className="absolute w-56 h-56 rounded-full border border-indigo-400/50 animate-[spin_14s_linear_infinite_reverse]" />
          <div className="absolute w-40 h-40 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-2xl shadow-blue-500/40 flex items-center justify-center">
            <div className="w-20 h-20 rounded-full bg-blue-300/20 backdrop-blur-sm border border-white/30 animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-[380px] sm:h-[450px] lg:h-[500px] flex items-center justify-center cursor-grab active:cursor-grabbing ${className}`}
      aria-label="VIGNAN-AI Interactive 3D Core"
      role="img"
    />
  );
};


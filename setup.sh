#!/bin/bash
set -e

echo "🚀 Cockpit Codespace Setup"
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize projects directory
PROJECTS_DIR="${WORKSPACE_ROOT:-$(pwd)}/projects"
echo -e "${BLUE}📁 Initializing projects directory: ${PROJECTS_DIR}${NC}"
mkdir -p "${PROJECTS_DIR}"

# Install Emscripten if not already installed
if [ ! -d "/opt/emsdk" ]; then
  echo -e "${BLUE}📦 Installing Emscripten SDK...${NC}"
  sudo mkdir -p /opt/emsdk
  sudo chown -R $(whoami):$(id -gn) /opt/emsdk
  cd /opt/emsdk
  git clone --depth 1 https://github.com/emscripten-core/emsdk.git .
  ./emsdk install latest
  ./emsdk activate latest
  echo -e "${GREEN}✅ Emscripten SDK installed${NC}"
else
  echo -e "${GREEN}✅ Emscripten SDK already installed${NC}"
fi

# Source Emscripten environment
if [ -f "/opt/emsdk/emsdk_env.sh" ]; then
  source /opt/emsdk/emsdk_env.sh
  # Add to bashrc for persistence
  if ! grep -q "emsdk_env.sh" ~/.bashrc; then
    echo 'source /opt/emsdk/emsdk_env.sh > /dev/null 2>&1' >> ~/.bashrc
  fi
fi

# Create placeholder projects
echo -e "${BLUE}🎨 Creating placeholder projects...${NC}"

# Example 1: WebGPU Graphics Demo
if [ ! -d "${PROJECTS_DIR}/webgpu-demo" ]; then
  mkdir -p "${PROJECTS_DIR}/webgpu-demo"
  cat > "${PROJECTS_DIR}/webgpu-demo/README.md" << 'EOF'
# WebGPU Graphics Demo

A starter project for WebGPU-based graphics programming.

## Features
- GPU-accelerated rendering
- Compute shaders
- Real-time performance

## Getting Started
```bash
npm install
npm run dev
```
EOF
  echo -e "${GREEN}✅ Created webgpu-demo${NC}"
fi

# Example 2: WASM Audio Processor
if [ ! -d "${PROJECTS_DIR}/wasm-audio" ]; then
  mkdir -p "${PROJECTS_DIR}/wasm-audio"
  cat > "${PROJECTS_DIR}/wasm-audio/README.md" << 'EOF'
# WASM Audio Processor

High-performance audio processing using WebAssembly.

## Features
- Real-time DSP
- Low-latency audio
- Optimized for 2-core systems

## Build
```bash
emcc audio.c -o audio.wasm -O3 -s WASM=1
```
EOF
  echo -e "${GREEN}✅ Created wasm-audio${NC}"
fi

# Example 3: Creative Code Sandbox
if [ ! -d "${PROJECTS_DIR}/sandbox" ]; then
  mkdir -p "${PROJECTS_DIR}/sandbox"
  cat > "${PROJECTS_DIR}/sandbox/README.md" << 'EOF'
# Creative Code Sandbox

Experimental space for creative coding projects.

## Purpose
- Quick prototyping
- Algorithm testing
- Creative experiments

## Tech Stack
- WebAssembly
- WebGPU
- Web Audio API
EOF
  echo -e "${GREEN}✅ Created sandbox${NC}"
fi

# Optimize for 2-core efficiency
echo -e "${BLUE}⚙️  Optimizing for 2-core efficiency...${NC}"

# Set CPU affinity for better performance on 2-core systems
if command -v taskset &> /dev/null; then
  echo "CPU affinity tools available"
fi

# Configure git for better performance
git config --global core.preloadindex true
git config --global core.fscache true
git config --global gc.auto 256

# Install common npm packages for AI/creative coding (optional, lightweight)
echo -e "${BLUE}📦 Installing common development tools...${NC}"

# Install lightweight global tools
if command -v npm &> /dev/null; then
  npm config set fetch-retries 3
  npm config set fetch-retry-mintimeout 10000
  npm config set fetch-retry-maxtimeout 60000
  echo -e "${GREEN}✅ npm configured${NC}"
fi

# Python packages
if command -v pip &> /dev/null; then
  pip install --upgrade pip --quiet
  echo -e "${GREEN}✅ pip updated${NC}"
fi

# Create a helpful info file
cat > "${PROJECTS_DIR}/INFO.md" << 'EOF'
# Cockpit Projects Directory

This directory contains your creative coding projects.

## Structure
- `webgpu-demo/` - WebGPU graphics programming
- `wasm-audio/` - WebAssembly audio processing
- `sandbox/` - Experimental playground

## Environment
- Node.js (LTS)
- Python 3.11
- Emscripten SDK
- Desktop environment (VNC)

## Optimization
This environment is optimized for:
- 2-core CPU efficiency
- AI context and code analysis
- Low-memory footprint
- Fast iteration cycles

## Tips
1. Keep projects modular and focused
2. Use WebAssembly for performance-critical code
3. Leverage WebGPU for parallel processing
4. Write AI-friendly, well-documented code

## Resources
- Emscripten: https://emscripten.org/
- WebGPU: https://gpuweb.github.io/gpuweb/
- Web Audio: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
EOF

echo ""
echo -e "${GREEN}✅ Cockpit Codespace setup complete!${NC}"
echo ""
echo -e "${YELLOW}🎯 Next steps:${NC}"
echo "  1. Open cockpit.code-workspace in VS Code"
echo "  2. Explore projects in the /projects directory"
echo "  3. Start building with WASM, WebGPU, and Audio APIs"
echo ""
echo -e "${BLUE}📚 Resources:${NC}"
echo "  - Projects: ${PROJECTS_DIR}"
echo "  - Emscripten: /opt/emsdk"
echo "  - Desktop: http://localhost:6080"
echo ""

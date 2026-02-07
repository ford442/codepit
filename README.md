# 🚀 Cockpit Codespace

A framework to start a codespace with tools for creative coding and project management ready.

## Overview

Cockpit is a fully-configured development environment optimized for:
- **WebAssembly (WASM)** development with Emscripten
- **WebGPU** graphics programming
- **Audio Logic** and real-time audio processing
- AI-friendly context and 2-core efficiency

## Features

### 🛠️ Development Tools
- **Node.js** (LTS) - JavaScript runtime
- **Python 3.11** - Scripting and AI tools
- **Emscripten** - C/C++ to WebAssembly compiler
- **Desktop Environment** - VNC access on port 6080

### 🎯 Optimizations
- **2-Core CPU** efficiency with resource limits
- **AI-Optimized** codebase structure for GitHub Copilot
- **Workspace Configuration** with root and projects mapping
- **Git Configuration** for performance

### 📁 Project Structure
```
codepit/
├── .devcontainer/          # Codespace configuration
│   └── devcontainer.json   # Node, Python, Emscripten, desktop-lite
├── .github/                # GitHub configuration
│   └── copilot-instructions.md  # Senior Creative Engineer persona
├── projects/               # Your creative projects (auto-created)
│   ├── webgpu-demo/        # WebGPU graphics demo
│   ├── wasm-audio/         # WASM audio processor
│   └── sandbox/            # Experimental playground
├── cockpit.code-workspace  # VS Code workspace config
├── setup.sh                # Setup script (runs automatically)
└── README.md               # This file
```

## Getting Started

### Option 1: GitHub Codespaces (Recommended)
1. Click the green "Code" button on GitHub
2. Select "Create codespace on main"
3. Wait for the environment to build (first time takes ~5 minutes)
4. The `setup.sh` script runs automatically
5. Open `cockpit.code-workspace` when prompted

### Option 2: Local VS Code with Dev Containers
1. Clone this repository
2. Open in VS Code
3. Install "Dev Containers" extension
4. Press F1 → "Dev Containers: Reopen in Container"
5. Wait for container to build
6. Open `cockpit.code-workspace`

## Usage

### Working with Projects
All your creative projects go in the `projects/` directory:
```bash
cd projects/
ls -la  # See placeholder projects
```

### Building WebAssembly
Use the built-in task or command line:
```bash
# Using emcc directly
emcc mycode.c -o mycode.wasm -O3 -s WASM=1

# Or use VS Code task: Ctrl+Shift+B → "Build WASM"
```

### Accessing Desktop Environment
- Open browser to: http://localhost:6080
- Password: `codespace`
- Use for GUI applications and visualization

### GitHub Copilot
The environment includes a Senior Creative Engineer persona that:
- Understands WASM, WebGPU, and Audio APIs
- Optimizes for 2-core systems
- Writes AI-friendly, well-documented code
- Balances performance with maintainability

## Configuration Files

### `.devcontainer/devcontainer.json`
Configures the development container with all necessary tools and features.

### `.github/copilot-instructions.md`
Defines the AI persona for GitHub Copilot assistance.

### `cockpit.code-workspace`
VS Code workspace with optimized settings and tasks.

### `setup.sh`
Automated setup script that:
- Installs Emscripten SDK
- Creates project directories
- Generates placeholder projects
- Optimizes system for 2-core efficiency

## Environment Variables
- `EMSDK` - Emscripten SDK path
- `EM_CONFIG` - Emscripten configuration
- `EM_CACHE` - Emscripten cache directory
- `WORKSPACE_ROOT` - Root workspace directory

## Tips

1. **Use the workspace file**: Open `cockpit.code-workspace` for the best experience
2. **Keep projects modular**: Each project in `projects/` should be self-contained
3. **Leverage WebAssembly**: Use C/C++ with Emscripten for performance-critical code
4. **Use WebGPU**: Take advantage of GPU acceleration for graphics and compute
5. **Write AI-friendly code**: Clear structure and documentation help Copilot assist better

## Troubleshooting

### Emscripten not found
```bash
source /opt/emsdk/emsdk_env.sh
```

### Projects directory missing
```bash
bash setup.sh
```

### Desktop not accessible
Check that port 6080 is forwarded in your codespace settings.

## Resources

- [Emscripten Documentation](https://emscripten.org/)
- [WebGPU Specification](https://gpuweb.github.io/gpuweb/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [GitHub Copilot](https://github.com/features/copilot)

## License

This framework is designed for creative coding and project management. Use it to build amazing things! 🎨✨

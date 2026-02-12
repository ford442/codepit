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
- **Aider** - AI-powered pair programming
- **Kimi** - AI-powered CLI tool
- **Emscripten 3.1.50** - C/C++ to WebAssembly compiler (pinned version)
- **Desktop Environment** - VNC access on port 6080 (configurable password)

### 🤖 Multi-Model AI Orchestration
- **Providers**: X.AI (Grok), Moonshot (Kimi), OpenAI, Anthropic (Claude)
- **Roles**: architect, coder, reviewer, researcher — auto-routed to best provider
- **Chain**: Sequential model refinement (model A → model B improves answer)
- **Consensus**: Multi-model voting with synthesized output
- **Delegate**: Role-based routing to the best provider
- **Pipeline**: Named multi-step workflows (e.g., research → implement → review)

### 🎯 Optimizations
- **2-Core CPU** efficiency with resource limits
- **8GB Memory** allocation for WebGPU and WASM workloads
- **AI-Optimized** codebase structure for GitHub Copilot
- **Workspace Configuration** with root and projects mapping
- **Git Configuration** for performance
- **Pinned Dependencies** for reproducible builds

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
├── models.json             # AI provider, role & pipeline definitions
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
- Default password: `codespace` (configurable via VNC_PASSWORD env variable)
- Use for GUI applications and visualization

### GitHub Copilot
The environment includes a Senior Creative Engineer persona that:
- Understands WASM, WebGPU, and Audio APIs
- Optimizes for 2-core systems
- Writes AI-friendly, well-documented code
- Balances performance with maintainability

### AI CLI & Multi-Model Orchestration
The `ai-cli.sh` script provides unified access to multiple AI providers and orchestration patterns:

```bash
# Single model queries
./ai-cli.sh xai "Explain WebGPU compute shaders"
./ai-cli.sh kimi "Optimize this Rust code"
./ai-cli.sh openai "Design a shader pipeline"
./ai-cli.sh anthropic "Review this C++ module"

# Chain: First model answers, second refines
./ai-cli.sh chain "Best approach for real-time audio in WASM?"

# Consensus: Ask all configured models, synthesize the best answer
./ai-cli.sh consensus "Should I use WebGPU or WebGL for particle effects?"

# Delegate: Route to the best provider for a specific role
./ai-cli.sh delegate coder "Write a WGSL vertex shader"
./ai-cli.sh delegate reviewer "Check this function for memory leaks"

# Pipeline: Run named multi-step workflows
./ai-cli.sh pipeline code-review "Add error handling to fetch calls"
./ai-cli.sh pipeline design-implement "Real-time audio visualizer"

# Management
./ai-cli.sh test        # Test all API connections
./ai-cli.sh models      # List available models
./ai-cli.sh roles       # List available roles
./ai-cli.sh pipelines   # List available pipelines
```

Providers, roles, and pipelines are configured in `models.json`. Add your API keys to `.env` (see `.env.example`).

## Documentation

- **[AGENTS.md](./AGENTS.md)** - Complete guide for AI assistants working in this codebase
- **[COMMANDS.md](./COMMANDS.md)** - Quick reference for all development commands
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Solutions for common issues

## Configuration Files

### `models.json`
Defines AI providers, roles (with system prompts and preferred providers), and named pipelines for multi-step orchestration.

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
- `VNC_PASSWORD` - Desktop VNC password (default: "codespace")

## Tips

1. **Use the workspace file**: Open `cockpit.code-workspace` for the best experience
2. **Read AGENTS.md**: Start with [AGENTS.md](./AGENTS.md) for full context
3. **Keep projects modular**: Each project in `projects/` should be self-contained
4. **Leverage WebAssembly**: Use C/C++ with Emscripten for performance-critical code
5. **Use WebGPU**: Take advantage of GPU acceleration for graphics and compute
6. **Write AI-friendly code**: Clear structure and documentation help Copilot assist better

## Troubleshooting

See **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** for comprehensive troubleshooting guide.

### Quick Fixes

#### Emscripten not found
```bash
source /opt/emsdk/emsdk_env.sh
emcc --version  # Should show 3.1.50
```

#### Projects directory missing
```bash
bash setup.sh
```

#### Desktop not accessible
1. Check that port 6080 is forwarded in your codespace settings
2. Verify VNC password is correct (default: "codespace")
3. Try accessing via the Ports tab in VS Code

#### Out of Memory During Build
```bash
# The codespace now has 8GB memory allocated
# If still having issues, close other applications
# or reduce optimization level:
emcc input.cpp -o output.js -O2  # Use -O2 instead of -O3
```

#### Vite Dev Server Not Starting
```bash
# Port 5173 is now forwarded by default
npm run dev
# Check the Ports tab in VS Code to access the server
```

#### WebGPU Not Available
- Requires Chrome 113+ or Edge 113+
- Check `chrome://gpu` for "WebGPU: Hardware accelerated"
- Ensure using secure context (HTTPS or localhost)

## Resources

- [Emscripten Documentation](https://emscripten.org/)
- [WebGPU Specification](https://gpuweb.github.io/gpuweb/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [GitHub Copilot](https://github.com/features/copilot)

## License

This framework is designed for creative coding and project management. Use it to build amazing things! 🎨✨

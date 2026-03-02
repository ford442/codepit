# Codepit - Cockpit Codespace Agent Guide

## Quick Orientation

- **Type**: Creative coding workspace with 12+ projects
- **Focus**: WebAssembly, WebGPU, Audio DSP, AI/ML inference
- **Tools**: Emscripten, Vite, React/TypeScript, Python FastAPI
- **Hardware target**: 2-core systems

## Repository Structure

```
codepit/
├── projects/               # Individual creative coding projects (git-ignored content)
│   ├── the_jokesters/     # Multi-agent chat with WebGPU LLM inference
│   ├── web_sequencer/     # Browser DAW (Hyphon) - React + WASM audio
│   ├── mod-player/        # ProTracker MOD player
│   ├── flac_player/       # FLAC audio player
│   └── ... (see repos.json for full list)
├── shared/                # Cross-project shared resources
│   └── hf/               # HuggingFace related utilities
├── .devcontainer/         # Codespace configuration
├── .github/              # Copilot instructions, issue templates
├── ai-cli.sh             # Multi-model AI orchestration script
├── dev.sh                # Primary development CLI
├── switch.sh             # Project context switching
├── setup.sh              # Environment setup & repo cloning
├── models.json           # AI provider configurations
├── repos.json            # Project registry
└── cockpit.code-workspace # VS Code workspace config
```

## Essential Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `./dev.sh start <repo>` | Clone, switch, and serve | `./dev.sh start web_sequencer` |
| `./dev.sh status` | Show status of all repos | - |
| `./dev.sh pull-all` | Pull latest for all cloned repos | - |
| `./dev.sh push-all` | Push all changes in all repos | - |
| `./ai-cli.sh <cmd>` | Multi-model AI orchestration | `./ai-cli.sh chain "optimize WASM"` |
| `./switch.sh <repo>` | Switch active project context | `./switch.sh the_jokesters` |
| `./setup.sh clone <repo>` | Clone from repos.json registry | `./setup.sh clone web_sequencer` |

### AI CLI Commands

```bash
# Single provider queries
./ai-cli.sh xai "Explain WebGPU compute shaders"
./ai-cli.sh kimi "Optimize this Rust code"
./ai-cli.sh openai "Design a shader pipeline"
./ai-cli.sh anthropic "Review this C++ module"

# Kimi shortcuts
./ai-cli.sh --kimi "Summarise this large document"         # one-shot Kimi assistant
./ai-cli.sh --kimi-swarm "Build a real-time audio visualiser"  # swarm decompose

# Orchestration patterns
./ai-cli.sh chain "Best approach for real-time audio in WASM?"
./ai-cli.sh consensus "WebGPU vs WebGL for particle effects?"
./ai-cli.sh delegate coder "Write a WGSL vertex shader"
./ai-cli.sh delegate reviewer "Check this function for memory leaks"
./ai-cli.sh pipeline code-review "Add error handling to fetch calls"
./ai-cli.sh pipeline design-implement "Real-time audio visualizer"
./ai-cli.sh pipeline kimi-assistant "Explain the Rubberband pitch-shift algorithm"
./ai-cli.sh pipeline kimi-swarm "Decompose and solve the MOD player rewrite"

# Management
./ai-cli.sh test        # Test all API connections
./ai-cli.sh models      # List available models
./ai-cli.sh roles       # List available roles
./ai-cli.sh pipelines   # List available pipelines
```

### Kimi Integration

Kimi (`kimi-pro`) is the primary long-context model with a **200 000-token context window**, ideal for:

- Summarising or reasoning over large codebases / documents
- Multi-step swarm decomposition (`--kimi-swarm`)
- Any task that exceeds the context limits of other providers

**Setup:**
```bash
# Recommended: set KIMI_API_KEY in your .env
KIMI_API_KEY=sk-...

# Legacy key name also accepted as a fallback
MOONSHOT_API_KEY=sk-...
```

**Optional: make Kimi the default model globally**
```bash
# In .env or shell profile
KIMI_DEFAULT=true   # forces kimi-pro for all kimi provider calls
```

**One-off assistant query (temp 0.2 – precise):**
```bash
./ai-cli.sh --kimi "What are the tradeoffs of SharedArrayBuffer vs MessageChannel?"
# equivalent to:
./ai-cli.sh pipeline kimi-assistant "<prompt>"
```

**Swarm / decompose pattern (temp 0.3 – creative):**
```bash
./ai-cli.sh --kimi-swarm "Rewrite the MOD player audio engine with AudioWorklet"
# equivalent to:
./ai-cli.sh pipeline kimi-swarm "<prompt>"
```

The swarm pipeline runs four roles sequentially — **planner → splitter → worker → summarizer** — each using Kimi with the pipeline temperature (0.3), so the final output is a consolidated, de-duplicated answer.

## Common Patterns Across Projects

### WebAssembly Build Patterns
| Source | Toolchain | Output | Use Case |
|--------|-----------|--------|----------|
| C/C++ | Emscripten (`emcc`) | `.wasm` + `.js` glue | High-performance DSP |
| Rust | `wasm-pack` | `.wasm` + ES modules | Safe systems code |
| AssemblyScript | `asc` | `.wasm` | TypeScript-like syntax |

### Audio Architecture Pattern
- **Web Audio API** - Master graph, scheduling
- **AudioWorklets** - Real-time processing in separate thread
- **WASM DSP** - Number crunching (oscillators, filters)
- **Emscripten** - C++ libraries (Rubberband pitch shifting)

### Frontend Stack Pattern
- **Vite** - Fast dev server, ESNext modules
- **React 19+** - UI components
- **TypeScript 5.9+** - Type safety
- **Tailwind CSS** - Styling

### 3D/Graphics Pattern
- **React Three Fiber** - React wrapper for Three.js
- **Three.js** - Direct WebGL when needed
- **WebGPU** - Compute shaders, massive parallelism
- **WGSL** - WebGPU shading language

## Key Configuration Files

| File | Purpose |
|------|---------|
| `models.json` | AI provider configs, roles (architect/coder/reviewer/researcher), pipelines |
| `repos.json` | Project registry - maps names to GitHub repos for dev.sh |
| `.env` | API keys (XAI_API_KEY, MOONSHOT_API_KEY, etc.) - see `.env.example` |
| `cockpit.code-workspace` | VS Code workspace with extensions and settings |
| `.github/copilot-instructions.md` | GitHub Copilot persona (Senior Creative Engineer) |

## When Working on Projects

1. **Check for project-level `AGENTS.md`** first - most projects have detailed guides
2. **Respect the `projects/` gitignore** - don't commit project files to codepit
3. **Activate Emscripten** when building C++ WASM:
   ```bash
   source /opt/emsdk/emsdk_env.sh
   ```
4. **GPU projects need Chrome/Edge** with WebGPU support (113+)
5. **Use `./dev.sh start <repo>`** to ensure proper context

## Project Quick Reference

| Project | Tech Stack | Key Features |
|---------|------------|--------------|
| `the_jokesters` | TypeScript, Vite, Three.js, @mlc-ai/web-llm | In-browser LLM, multi-agent chat, TTS |
| `web_sequencer` | React, TypeScript, WASM, WebGPU | DAW with synthesizers, sampler, sequencer |
| `mod-player` | JavaScript, WASM | ProTracker MOD file playback |
| `flac_player` | JavaScript, Web Audio API | FLAC streaming player |
| `image_video_effects` | WebGL/Canvas | Real-time image/video filters |
| `watershed` | WebAssembly | Audio analysis/visualization |

## Troubleshooting

### Emscripten not found
```bash
source /opt/emsdk/emsdk_env.sh
```

### WebGPU not working
- Requires Chrome 113+ or Edge 113+
- Check `chrome://gpu` for WebGPU support
- Some features need secure context (HTTPS/localhost)

### Project not showing up in dev.sh
- Check it's cloned: `ls ~/projects/`
- Run: `./setup.sh clone <repo-name>`
- Verify it's in `repos.json`

### Out of memory during build
- 2-core codespace limit - build WASM separately
- Close other projects: `./dev.sh stop <other-repo>`
- Use lite build if available: `npm run build:lite`

### AI CLI not working
- Check `.env` has required API keys
- Test with: `./ai-cli.sh test`
- Individual provider keys: XAI_API_KEY, KIMI_API_KEY (or MOONSHOT_API_KEY), OPENAI_API_KEY, ANTHROPIC_API_KEY
- For Kimi: `KIMI_API_KEY` is checked first; `MOONSHOT_API_KEY` is the fallback

## Development Workflow

### Starting a new session
```bash
# See what's already cloned
./dev.sh status

# Start working on a project
./dev.sh start web_sequencer
# This clones (if needed), switches context, and starts dev server

# In another terminal - work on a second project
./dev.sh start the_jokesters
```

### Making changes across multiple projects
```bash
# Pull all updates
./dev.sh pull-all

# Make changes...

# Push all changes (commits each repo separately)
./dev.sh push-all

# Or create PR for specific repo
./dev.sh pr web_sequencer "Fix audio crackling issue"
```

### Using multi-model AI
```bash
# Get architecture advice
./ai-cli.sh delegate architect "How should I structure a real-time audio engine?"

# Then implement it
./ai-cli.sh delegate coder "Write a Web Audio API scheduler with lookahead"

# Review the result
./ai-cli.sh delegate reviewer "Check this audio worklet for buffer underruns"
```

## Environment Variables

Required in `.env` (see `.env.example`):
```bash
# AI Providers (at least one needed for ai-cli.sh)
XAI_API_KEY=...
KIMI_API_KEY=...          # Kimi / Moonshot — primary key
MOONSHOT_API_KEY=...      # Accepted as fallback if KIMI_API_KEY is unset
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# Optional Kimi behaviour
KIMI_DEFAULT=true         # Always use kimi-pro as the Kimi model

# Cloud Storage (for projects using it)
GCP_BUCKET_NAME=...
GCP_CREDENTIALS=...  # JSON string or path

# Deployment (for projects with deploy scripts)
DEPLOY_HOST=...
DEPLOY_USER=...
DEPLOY_KEY=...
```

## Resources

- [Emscripten Documentation](https://emscripten.org/)
- [WebGPU Specification](https://gpuweb.github.io/gpuweb/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [AssemblyScript](https://www.assemblyscript.org/)
- [Rust WASM](https://rustwasm.github.io/)

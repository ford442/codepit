🛸 The Cockpit
An Agent-Centric Development Environment for Creative Engineering.

This repository serves as a persistent, high-performance "Laboratory" for WASM, WebGPU, and Audio/AI projects. Instead of isolated environments, this Cockpit centralizes your tooling, AI personas, and cross-project logic.

🏗️ Architecture
/projects: All active work repositories are cloned here.

.devcontainer/: A "Fat" container optimized for 2-core efficiency, pre-loaded with Emscripten, Node.js, and Python.

.github/copilot-instructions.md: Global system prompts that define your coding standards (Performance-first, Functional, Modular).

cockpit.code-workspace: The master file that bridges all cloned projects into one cohesive VS Code sidebar.

🚀 Getting Started
Launch: Open this repo in a GitHub Codespace.

Initialize: Run the setup script to prepare your project directory:

Bash
chmod +x setup.sh && ./setup.sh
Open Workspace: When prompted, click "Open Workspace" or open cockpit.code-workspace. This enables multi-repo AI indexing.

🛠️ Adding a New Project
To bring a new project into the Cockpit's context:

Open the terminal.

cd projects

git clone <your-repo-url>

The cockpit.code-workspace will automatically detect the new folder and include it in Copilot Chat's @workspace scope.

🧠 AI Intelligence
This environment is pre-configured to understand the "Noah Cohn" engineering style:

High Performance: Prioritizes C++/WASM interop and shader optimization.

Creative Logic: Understands modular audio sequencers and visualizer patterns.

Persistence: Your custom @agent files in /agents provide specific guidance for complex math or API quirks.

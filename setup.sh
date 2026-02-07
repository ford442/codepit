#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECTS_DIR="${HOME}/projects"
REPOS_FILE="${WORKSPACE_ROOT:-$(dirname "$0")}/repos.json"
GITHUB_USER="ford442"

show_help() {
    echo "🚀 Cockpit Codespace Setup"
    echo "=========================="
    echo ""
    echo "Usage: ./setup.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  (no args)         - Run initial setup"
    echo "  clone <repo>      - Clone a specific repo"
    echo "  clone-all         - Clone all repos in registry"
    echo "  list              - List available repos"
    echo "  status            - Show status of all cloned repos"
    echo "  help              - Show this help"
    echo ""
    echo "Examples:"
    echo "  ./setup.sh clone candy_world"
    echo "  ./setup.sh clone-all"
    echo "  ./setup.sh status"
}

list_repos() {
    echo -e "${BLUE}📋 Available Repositories:${NC}"
    echo ""
    if command -v jq &> /dev/null; then
        jq -r '.registry | to_entries[] | "  \(.key) - \(.value.description) [\(.value.stack | join(", "))]"' "$REPOS_FILE"
    else
        echo "  Install jq for formatted output: apt-get install jq"
    fi
    echo ""
}

clone_repo() {
    local repo_name=$1
    local repo_url="https://github.com/${GITHUB_USER}/${repo_name}.git"
    local target_dir="${PROJECTS_DIR}/${repo_name}"
    
    local default_branch="main"
    local build_cmd=""
    if command -v jq &> /dev/null; then
        default_branch=$(jq -r ".registry[\"$repo_name\"].default_branch // \"main\"" "$REPOS_FILE" 2>/dev/null)
        build_cmd=$(jq -r ".registry[\"$repo_name\"].build_cmd // \"\"" "$REPOS_FILE" 2>/dev/null)
    fi
    
    if [ -d "$target_dir/.git" ]; then
        echo -e "${YELLOW}⚠️  ${repo_name} already cloned. Pulling latest...${NC}"
        cd "$target_dir"
        git pull origin "$default_branch"
    else
        echo -e "${BLUE}📥 Cloning ${repo_name}...${NC}"
        mkdir -p "$PROJECTS_DIR"
        git clone "$repo_url" "$target_dir"
        cd "$target_dir"
        echo -e "${GREEN}✅ Cloned to ${target_dir}${NC}"
    fi
    
    if [ -n "$build_cmd" ] && [ "$build_cmd" != "null" ]; then
        echo -e "${BLUE}📦 Installing dependencies...${NC}"
        (cd "$target_dir" && bash -c "$build_cmd") || \
            echo -e "${YELLOW}⚠️  Build command failed, you may need to run it manually${NC}"
    fi
    
    echo -e "${GREEN}✅ ${repo_name} ready!${NC}"
    echo ""
}

clone_all() {
    echo -e "${BLUE}📥 Cloning all repos...${NC}"
    echo ""
    
    if command -v jq &> /dev/null; then
        jq -r '.registry | keys[]' "$REPOS_FILE" | while read -r repo; do
            clone_repo "$repo"
        done
    else
        echo -e "${YELLOW}⚠️  jq not found. Install jq or clone repos individually:${NC}"
        list_repos
    fi
}

show_status() {
    echo -e "${BLUE}📊 Repo Status:${NC}"
    echo ""
    
    if command -v jq &> /dev/null; then
        jq -r '.registry | keys[]' "$REPOS_FILE" | while read -r repo; do
            local target_dir="${PROJECTS_DIR}/${repo}"
            if [ -d "$target_dir/.git" ]; then
                cd "$target_dir"
                local branch=$(git branch --show-current)
                local changes=$(git status --porcelain | wc -l)
                local unpushed=$(git log origin/$branch..HEAD --oneline 2>/dev/null | wc -l)
                
                if [ "$changes" -gt 0 ]; then
                    echo -e "  ${YELLOW}⚠️  ${repo} [${branch}] - ${changes} uncommitted changes${NC}"
                elif [ "$unpushed" -gt 0 ]; then
                    echo -e "  ${BLUE}⬆️  ${repo} [${branch}] - ${unpushed} unpushed commits${NC}"
                else
                    echo -e "  ${GREEN}✅ ${repo} [${branch}] - clean${NC}"
                fi
            else
                echo -e "  ${RED}❌ ${repo} - not cloned${NC}"
            fi
        done
    else
        echo "  Install jq for status: apt-get install jq"
    fi
    echo ""
}

initial_setup() {
    echo "🚀 Cockpit Codespace Setup"
    echo "=========================="
    echo ""
    
    # Install jq if not present
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}📦 Installing jq...${NC}"
        sudo apt-get update && sudo apt-get install -y jq
    fi
    
    # Load or fetch environment variables
    local ENV_FILE="${WORKSPACE_ROOT:-$(dirname "$0")}/.env"
    local ENV_REMOTE_FILE="${WORKSPACE_ROOT:-$(dirname "$0")}/.env.remote"
    
    if [ -f "$ENV_FILE" ]; then
        echo -e "${BLUE}🔐 Loading API keys from .env...${NC}"
        set -a
        source "$ENV_FILE"
        set +a
        echo -e "${GREEN}✅ Environment loaded${NC}"
        echo ""
    elif [ -f "$ENV_REMOTE_FILE" ]; then
        # Check if remote URL is configured
        local remote_url=$(grep -E '^URL=' "$ENV_REMOTE_FILE" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" | head -1)
        if [ -n "$remote_url" ]; then
            echo -e "${BLUE}🔐 Fetching secrets from remote...${NC}"
            if [ -f "${WORKSPACE_ROOT:-$(dirname "$0")}/fetch-secrets.sh" ]; then
                bash "${WORKSPACE_ROOT:-$(dirname "$0")}/fetch-secrets.sh" "$remote_url"
                echo ""
            else
                echo -e "${YELLOW}⚠️  fetch-secrets.sh not found${NC}"
            fi
        fi
    fi
    
    # Initialize projects directory
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
        if ! grep -q "emsdk_env.sh" ~/.bashrc; then
            echo 'source /opt/emsdk/emsdk_env.sh > /dev/null 2>&1' >> ~/.bashrc
        fi
    fi
    
    # Install jq if not present
    if ! command -v jq &> /dev/null; then
        echo -e "${BLUE}📦 Installing jq...${NC}"
        sudo apt-get update && sudo apt-get install -y jq
    fi
    
    # Setup shared cache directories
    echo -e "${BLUE}⚙️  Setting up shared caches...${NC}"
    mkdir -p "${HOME}/.npm-global"
    npm config set prefix "${HOME}/.npm-global"
    export PATH="${HOME}/.npm-global/bin:$PATH"
    
    # Configure git
    git config --global core.preloadindex true
    git config --global core.fscache true
    git config --global gc.auto 256
    
    # Install global tools
    if command -v npm &> /dev/null; then
        npm config set fetch-retries 3
        npm config set fetch-retry-mintimeout 10000
        npm config set fetch-retry-maxtimeout 60000
        npm install -g http-server serve typescript 2>/dev/null || true
        echo -e "${GREEN}✅ Global npm tools installed${NC}"
    fi
    
    if command -v pip &> /dev/null; then
        pip install --upgrade pip --quiet
        echo -e "${GREEN}✅ pip updated${NC}"
    fi
    
    # Make .env auto-load in shell profile
    if ! grep -q "source.*\.env" "${HOME}/.bashrc" 2>/dev/null; then
        echo '' >> "${HOME}/.bashrc"
        echo '# Load Cockpit environment' >> "${HOME}/.bashrc"
        echo "set -a; source ${WORKSPACE_ROOT}/.env 2>/dev/null || true; set +a" >> "${HOME}/.bashrc"
        echo "alias ai='${WORKSPACE_ROOT}/ai-cli.sh'" >> "${HOME}/.bashrc"
        echo -e "${GREEN}✅ Added .env loader and 'ai' alias to .bashrc${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Cockpit Codespace setup complete!${NC}"
    echo ""
    echo -e "${YELLOW}🎯 Next steps:${NC}"
    echo "  1. View available repos: ./setup.sh list"
    echo "  2. Clone a repo: ./setup.sh clone candy_world"
    echo "  3. Clone all repos: ./setup.sh clone-all"
    echo "  4. Check status: ./setup.sh status"
    echo "  5. Switch to a project: ./switch.sh candy_world"
    echo ""
    echo -e "${BLUE}📚 Resources:${NC}"
    echo "  - Projects: ${PROJECTS_DIR}"
    echo "  - Repos config: ${REPOS_FILE}"
    echo "  - Emscripten: /opt/emsdk"
    echo ""
}

# Main command dispatcher
case "${1:-}" in
    clone)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Please specify a repo name${NC}"
            list_repos
            exit 1
        fi
        clone_repo "$2"
        ;;
    clone-all)
        clone_all
        ;;
    list)
        list_repos
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        initial_setup
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac

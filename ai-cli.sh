#!/bin/bash
# AI CLI Helper - Quick access to X.AI and Moonshot APIs

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_help() {
    echo "🤖 AI CLI Helper"
    echo "================"
    echo ""
    echo "Quick access to your configured AI APIs."
    echo ""
    echo "Environment Variables:"
    echo "  XAI_API_KEY       - X.AI (Grok) API key"
    echo "  MOONSHOT_API_KEY  - Moonshot (Kimi) API key"
    echo ""
    echo "Usage:"
    echo "  ./ai-cli.sh xai <prompt>       - Query X.AI (Grok)"
    echo "  ./ai-cli.sh kimi <prompt>      - Query Moonshot (Kimi)"
    echo "  ./ai-cli.sh test               - Test all API connections"
    echo "  ./ai-cli.sh models             - List available models"
    echo ""
    echo "Examples:"
    echo '  ./ai-cli.sh xai "Explain WebGPU compute shaders"'
    echo '  ./ai-cli.sh kimi "Optimize this Rust code"'
}

test_apis() {
    echo -e "${BLUE}🧪 Testing API connections...${NC}"
    echo ""
    
    if [ -n "$XAI_API_KEY" ]; then
        echo -e "${BLUE}Testing X.AI...${NC}"
        local xai_response=$(curl -s -o /dev/null -w "%{http_code}" \
            https://api.x.ai/v1/models \
            -H "Authorization: Bearer $XAI_API_KEY" \
            -H "Content-Type: application/json" 2>/dev/null || echo "000")
        
        if [ "$xai_response" = "200" ]; then
            echo -e "  ${GREEN}✅ X.AI API connection successful${NC}"
        else
            echo -e "  ${YELLOW}⚠️  X.AI API returned HTTP $xai_response${NC}"
        fi
    else
        echo -e "  ${RED}❌ XAI_API_KEY not set${NC}"
    fi
    
    echo ""
    
    if [ -n "$MOONSHOT_API_KEY" ]; then
        echo -e "${BLUE}Testing Moonshot (Kimi)...${NC}"
        local kimi_response=$(curl -s -o /dev/null -w "%{http_code}" \
            https://api.moonshot.cn/v1/models \
            -H "Authorization: Bearer $MOONSHOT_API_KEY" \
            -H "Content-Type: application/json" 2>/dev/null || echo "000")
        
        if [ "$kimi_response" = "200" ]; then
            echo -e "  ${GREEN}✅ Moonshot API connection successful${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Moonshot API returned HTTP $kimi_response${NC}"
        fi
    else
        echo -e "  ${RED}❌ MOONSHOT_API_KEY not set${NC}"
    fi
}

list_models() {
    echo -e "${BLUE}📋 Available Models:${NC}"
    echo ""
    
    echo -e "X.AI (Grok):"
    if [ -n "$XAI_API_KEY" ]; then
        curl -s https://api.x.ai/v1/models \
            -H "Authorization: Bearer $XAI_API_KEY" \
            -H "Content-Type: application/json" 2>/dev/null | \
            jq -r '.data[] | "  - \(.id): \(.object)"' 2>/dev/null || \
            echo "  (Could not fetch models - check API key)"
    else
        echo "  ${YELLOW}API key not configured${NC}"
    fi
    
    echo ""
    echo -e "Moonshot (Kimi):"
    if [ -n "$MOONSHOT_API_KEY" ]; then
        curl -s https://api.moonshot.cn/v1/models \
            -H "Authorization: Bearer $MOONSHOT_API_KEY" \
            -H "Content-Type: application/json" 2>/dev/null | \
            jq -r '.data[] | "  - \(.id): \(.owned_by)"' 2>/dev/null || \
            echo "  (Could not fetch models - check API key)"
    else
        echo "  ${YELLOW}API key not configured${NC}"
    fi
}

query_xai() {
    local prompt="$1"
    if [ -z "$prompt" ]; then
        echo -e "${RED}Error: Please provide a prompt${NC}"
        exit 1
    fi
    
    if [ -z "$XAI_API_KEY" ]; then
        echo -e "${RED}Error: XAI_API_KEY not set${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🤖 Querying X.AI (Grok)...${NC}"
    echo ""
    
    curl -s https://api.x.ai/v1/chat/completions \
        -H "Authorization: Bearer $XAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"messages\": [
                {\"role\": \"system\", \"content\": \"You are a helpful assistant.\"},
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"model\": \"grok-beta\",
            \"stream\": false
        }" | jq -r '.choices[0].message.content // .error.message' 2>/dev/null || \
        echo "Error: Could not parse response"
}

query_kimi() {
    local prompt="$1"
    if [ -z "$prompt" ]; then
        echo -e "${RED}Error: Please provide a prompt${NC}"
        exit 1
    fi
    
    if [ -z "$MOONSHOT_API_KEY" ]; then
        echo -e "${RED}Error: MOONSHOT_API_KEY not set${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🌙 Querying Moonshot (Kimi)...${NC}"
    echo ""
    
    curl -s https://api.moonshot.cn/v1/chat/completions \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"moonshot-v1-8k\",
            \"messages\": [
                {\"role\": \"system\", \"content\": \"You are Kimi, a helpful assistant.\"},
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"temperature\": 0.3
        }" | jq -r '.choices[0].message.content // .error.message' 2>/dev/null || \
        echo "Error: Could not parse response"
}

case "${1:-}" in
    xai|grok)
        shift
        query_xai "$*"
        ;;
    kimi|moonshot)
        shift
        query_kimi "$*"
        ;;
    test)
        test_apis
        ;;
    models)
        list_models
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        echo -e "${RED}Error: Please specify a command${NC}"
        show_help
        exit 1
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac

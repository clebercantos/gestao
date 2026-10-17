#!/usr/bin/env bash
# Video AI Pack — instalador (macOS / Linux / WSL / Git Bash)
#
#   ./install.sh                       # skills + hook automático + CLAUDE.md + deps Python
#   ./install.sh --mcp all             # + todos os MCPs (Premiere, AE, Resolve, OpusClip, invideo, Higgsfield)
#   ./install.sh --mcp premiere,ae     # só os MCPs escolhidos
#   ./install.sh --community           # + skills da comunidade (Remotion, auto-editor, motion-design LobzyJay)
#   ./install.sh --uninstall
#
# Variáveis: CLAUDE_HOME (padrão ~/.claude), SKIP_PIP=1 para não instalar pacotes Python.
set -euo pipefail

PACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
HOOK_DIR="$CLAUDE_HOME/hooks/video-ai-pack"
SKILLS=(video-orquestrador video-decupagem video-colorgrade video-legendas video-motion video-entrega)
MCP_LIST=""
COMMUNITY=0
UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mcp) MCP_LIST="$2"; shift 2 ;;
    --community) COMMUNITY=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "opção desconhecida: $1" >&2; exit 1 ;;
  esac
done

say()  { printf '\033[1;35m▸\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*"; }
has()  { command -v "$1" >/dev/null 2>&1; }

PY=python3; has python3 || PY=python
has "$PY" || { echo "Python 3.9+ é obrigatório" >&2; exit 1; }

settings_hook() {  # $1 = add|remove
  "$PY" - "$CLAUDE_HOME/settings.json" "$HOOK_DIR/video_intent.py" "$1" "$PY" <<'EOF'
import json, sys, pathlib
path, script, mode, py = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
data = json.loads(path.read_text()) if path.exists() and path.read_text().strip() else {}
hooks = data.setdefault("hooks", {})
groups = [g for g in hooks.get("UserPromptSubmit", [])
          if not any("video_intent.py" in h.get("command", "") for h in g.get("hooks", []))]
if mode == "add":
    groups.append({"hooks": [{"type": "command", "command": f'{py} "{script}"', "timeout": 10}]})
if groups:
    hooks["UserPromptSubmit"] = groups
else:
    hooks.pop("UserPromptSubmit", None)
if not hooks:
    data.pop("hooks", None)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
EOF
}

claude_md() {  # $1 = add|remove
  local f="$CLAUDE_HOME/CLAUDE.md"
  touch "$f"
  "$PY" - "$f" "$PACK_DIR/config/CLAUDE.md.snippet" "$1" <<'EOF'
import re, sys, pathlib
f, snip, mode = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
txt = re.sub(r"\n?<!-- video-ai-pack:start -->.*?<!-- video-ai-pack:end -->\n?", "\n", f.read_text(), flags=re.S)
if mode == "add":
    txt = txt.rstrip() + "\n\n<!-- video-ai-pack:start -->\n" + snip.read_text().strip() + "\n<!-- video-ai-pack:end -->\n"
f.write_text(txt.lstrip("\n"))
EOF
}

if [[ $UNINSTALL == 1 ]]; then
  say "Removendo Video AI Pack de $CLAUDE_HOME"
  for s in "${SKILLS[@]}"; do rm -rf "$CLAUDE_HOME/skills/$s"; done
  rm -rf "$HOOK_DIR"
  settings_hook remove
  claude_md remove
  if has claude; then
    for m in premiere-pro aftereffects davinci-resolve opusclip invideo higgsfield; do
      claude mcp remove --scope user "$m" >/dev/null 2>&1 || true
    done
  fi
  say "Pronto."
  exit 0
fi

# 1. Dependências
say "Checando dependências"
has ffmpeg && has ffprobe || warn "ffmpeg/ffprobe não encontrado — instale (brew install ffmpeg | apt install ffmpeg | winget install Gyan.FFmpeg)"
has node || warn "Node.js 20+ não encontrado — necessário para os MCPs de Premiere/After Effects"
has claude || warn "CLI 'claude' não encontrada — MCPs não serão registrados automaticamente"
if [[ "${SKIP_PIP:-0}" != 1 ]]; then
  say "Instalando pacotes Python (faster-whisper, auto-editor)"
  "$PY" -m pip install --user --quiet --upgrade faster-whisper auto-editor 2>/dev/null \
    || "$PY" -m pip install --user --quiet --upgrade --break-system-packages faster-whisper auto-editor \
    || warn "pip falhou — instale manualmente: pip install faster-whisper auto-editor"
fi

# 2. Skills
say "Instalando skills em $CLAUDE_HOME/skills"
mkdir -p "$CLAUDE_HOME/skills"
for s in "${SKILLS[@]}"; do
  rm -rf "$CLAUDE_HOME/skills/$s"
  cp -R "$PACK_DIR/skills/$s" "$CLAUDE_HOME/skills/$s"
done
find "$CLAUDE_HOME/skills" -path '*video-*/scripts/*.py' -exec chmod +x {} +

# 3. Hook de roteamento automático + aprimoramento de prompt
say "Registrando hook UserPromptSubmit (detecção automática de pedidos de vídeo)"
mkdir -p "$HOOK_DIR"
cp "$PACK_DIR/hooks/video_intent.py" "$HOOK_DIR/"
chmod +x "$HOOK_DIR/video_intent.py"
settings_hook add

# 4. Instruções globais
say "Adicionando regras do pack em $CLAUDE_HOME/CLAUDE.md"
claude_md add

# 5. MCPs
add_mcp() {
  local name="$1"; shift
  claude mcp remove --scope user "$name" >/dev/null 2>&1 || true
  if claude mcp add --scope user "$@"; then say "MCP $name registrado"; else warn "falha ao registrar MCP $name"; fi
}
if [[ -n "$MCP_LIST" ]] && has claude; then
  [[ "$MCP_LIST" == all ]] && MCP_LIST="premiere,ae,resolve,opusclip,invideo,higgsfield"
  IFS=',' read -ra M <<< "$MCP_LIST"
  for m in "${M[@]}"; do
    case "$m" in
      premiere)
        add_mcp premiere-pro premiere-pro -- npx -y premiere-pro-mcp
        npx -y premiere-pro-mcp --install-cep || warn "rode depois: npx -y premiere-pro-mcp --install-cep (painel CEP do Premiere)" ;;
      ae)
        add_mcp aftereffects aftereffects -- npx -y @kumoproductions/mcp-aftereffects
        warn "After Effects: ative Preferences > Scripting & Expressions > 'Allow Scripts to Write Files and Access Network'" ;;
      resolve)
        "$PY" -m pip install --user --quiet davinci-resolve-mcp 2>/dev/null \
          || "$PY" -m pip install --user --quiet --break-system-packages davinci-resolve-mcp || true
        add_mcp davinci-resolve davinci-resolve -- davinci-resolve-mcp
        warn "Resolve 21.1+ também tem MCP oficial — veja README (seção Resolve)" ;;
      opusclip)   add_mcp opusclip --transport http opusclip https://mcp.opus.pro/mcp ;;
      invideo)    add_mcp invideo --transport http invideo https://mcp.invideo.io/mcp ;;
      higgsfield) add_mcp higgsfield --transport http higgsfield https://mcp.higgsfield.ai/mcp ;;
      *) warn "MCP desconhecido: $m" ;;
    esac
  done
  say "MCPs remotos pedem login OAuth: abra o Claude Code e rode /mcp"
fi

# 6. Skills da comunidade
if [[ $COMMUNITY == 1 ]]; then
  say "Instalando skills da comunidade"
  if has npx; then
    npx -y skills add remotion-dev/skills || warn "remotion skills falharam"
    npx -y skills add WyattBlue/auto-editor || warn "auto-editor skill falhou"
  fi
  if has git; then
    tmp="$(mktemp -d)"
    git clone --depth 1 https://github.com/LobzyJay/motion-design-with-claude.git "$tmp/mdc" \
      && cp -R "$tmp/mdc/skills/." "$CLAUDE_HOME/skills/" \
      || warn "motion-design-with-claude falhou"
    rm -rf "$tmp"
  fi
fi

say "Video AI Pack instalado. Reinicie o Claude Code e teste:"
echo '   "decupa o video.mp4, colorgrade cinematic e legenda karaokê pra Reels"'

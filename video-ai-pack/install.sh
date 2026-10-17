#!/usr/bin/env bash
# Video AI Pack — instalador (macOS / Linux / WSL / Git Bash)
#
#   ./install.sh                       # skills + hook automático + CLAUDE.md + deps Python
#   ./install.sh --mcp all             # + todos os MCPs (Premiere, AE, Resolve, OpusClip, invideo, Higgsfield)
#   ./install.sh --mcp premiere,ae     # só os MCPs escolhidos
#   ./install.sh --apps premiere,resolve,aftereffects --apis elevenlabs   # apps/APIs que você usa (roteador)
#   ./install.sh --budget 7000         # orçamento de tokens por pedido de vídeo (padrão 7000)
#   ./install.sh --no-sync             # não baixa o cofre das 100 skills agora
#   ./install.sh --community           # + instala de verdade as skills completas mais usadas (Remotion, auto-editor, LobzyJay)
#   ./install.sh --uninstall
#
# Variáveis: CLAUDE_HOME (padrão ~/.claude), SKIP_PIP=1 para não instalar pacotes Python.
set -euo pipefail

PACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
PACK_HOME="$CLAUDE_HOME/video-ai-pack"
OLD_HOOK_DIR="$CLAUDE_HOME/hooks/video-ai-pack"
SKILLS=(video-orquestrador video-decupagem video-colorgrade video-legendas video-motion video-entrega video-audio)
MCP_LIST=""
COMMUNITY=0
UNINSTALL=0
SYNC=1
CFG_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mcp) MCP_LIST="$2"; shift 2 ;;
    --community) COMMUNITY=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --no-sync) SYNC=0; shift ;;
    --apps|--apis|--budget) CFG_ARGS+=("$1" "$2"); shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "opção desconhecida: $1" >&2; exit 1 ;;
  esac
done

say()  { printf '\033[1;35m▸\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*"; }
has()  { command -v "$1" >/dev/null 2>&1; }

PY=python3; has python3 || PY=python
has "$PY" || { echo "Python 3.9+ é obrigatório" >&2; exit 1; }

settings_hook() {  # $1 = add|remove — hooks do pack: roteador de vídeo, memória e registro de conversas
  "$PY" - "$CLAUDE_HOME/settings.json" "$PACK_HOME" "$1" "$PY" <<'EOF'
import json, sys, pathlib
path, home, mode, py = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
OURS = {"UserPromptSubmit": ["video_intent.py", "memoria_hook.py"], "SessionEnd": ["registrar_conversa.py"]}
data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() and path.read_text(encoding="utf-8-sig").strip() else {}
hooks = data.setdefault("hooks", {})
for event, scripts in OURS.items():
    groups = [g for g in hooks.get(event, [])
              if not any(sc in h.get("command", "") for h in g.get("hooks", []) for sc in scripts)]
    if mode == "add":
        for sc in scripts:
            groups.append({"hooks": [{"type": "command", "command": f'{py} "{pathlib.Path(home) / sc}"', "timeout": 10 if event != "SessionEnd" else 30}]})
    if groups:
        hooks[event] = groups
    else:
        hooks.pop(event, None)
if not hooks:
    data.pop("hooks", None)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
  rm -rf "$PACK_HOME" "$OLD_HOOK_DIR"
  say "A pasta $CLAUDE_HOME/memoria foi mantida (é sua memória). Apague manualmente se quiser."
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

# 3. Roteador + catálogo top-100 + hook automático
say "Instalando roteador e catálogo das 100 skills em $PACK_HOME"
rm -rf "$OLD_HOOK_DIR"
mkdir -p "$PACK_HOME"
cp "$PACK_DIR/tools/pack.py" "$PACK_DIR"/hooks/*.py "$PACK_DIR/catalogo/skills.json" "$PACK_HOME/"
chmod +x "$PACK_HOME"/*.py
[[ ${#CFG_ARGS[@]} -gt 0 ]] && "$PY" "$PACK_HOME/pack.py" config "${CFG_ARGS[@]}" >/dev/null
if [[ $SYNC == 1 ]]; then
  say "Baixando o cofre (SKILL.md das 100 skills, ~1 MB — fora de ~/.claude/skills, custo fixo zero)"
  "$PY" "$PACK_HOME/pack.py" sync || warn "sync falhou — rode depois: $PY $PACK_HOME/pack.py sync"
fi
say "Registrando hooks: roteamento de vídeo, memória (correções) e registro de conversas"
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
        add_mcp premiere-pro premiere-pro -- npx -y premiere-pro-mcp@latest
        npx -y premiere-pro-mcp@latest --install-cep || warn "rode depois: npx -y premiere-pro-mcp --install-cep (painel CEP do Premiere)" ;;
      ae)
        add_mcp aftereffects aftereffects -- npx -y @kumoproductions/mcp-aftereffects@latest
        warn "After Effects: ative Preferences > Scripting & Expressions > 'Allow Scripts to Write Files and Access Network'" ;;
      resolve)
        # samuelgursky (o pacote PyPI davinci-resolve-mcp é outro projeto e quebra com mcp 2.x)
        echo 0 | npx -y davinci-resolve-mcp setup || true
        RD="${XDG_DATA_HOME:-$HOME/.local/share}/davinci-resolve-mcp"; [ -d "$HOME/Library/Application Support/davinci-resolve-mcp" ] && RD="$HOME/Library/Application Support/davinci-resolve-mcp"
        add_mcp davinci-resolve davinci-resolve -- "$RD/venv/bin/python" "$RD/src/server.py"
        warn "Resolve: Preferences > General > 'External scripting using' = Local" ;;
      opusclip)   add_mcp opusclip --transport http opusclip https://mcp.opus.pro/mcp ;;
      invideo)    add_mcp invideo --transport http invideo https://mcp.invideo.io/mcp ;;
      higgsfield) add_mcp higgsfield --transport http higgsfield https://mcp.higgsfield.ai/mcp ;;
      *) warn "MCP desconhecido: $m" ;;
    esac
  done
  say "MCPs remotos pedem login OAuth: abra o Claude Code e rode /mcp"
fi

# 6. Skills completas (com scripts/references) das mais usadas — o resto fica no cofre, sob demanda
if [[ $COMMUNITY == 1 ]]; then
  say "Instalando skills completas da comunidade"
  if has npx; then
    npx -y skills add https://github.com/remotion-dev/skills || warn "remotion skills falharam"
    npx -y skills add https://github.com/WyattBlue/auto-editor || warn "auto-editor skill falhou"
  fi
  if has git; then
    tmp="$(mktemp -d)"
    git clone --depth 1 https://github.com/LobzyJay/motion-design-with-claude.git "$tmp/mdc" \
      && cp -R "$tmp/mdc/skills/." "$CLAUDE_HOME/skills/" \
      || warn "motion-design-with-claude falhou"
    rm -rf "$tmp"
  fi
fi

# Memória permanente: ~/.claude/memoria (memoria.md nunca é sobrescrita; skills/mcps/agentes.md são regenerados)
say "Gerando memória e MDs de consulta em $CLAUDE_HOME/memoria"
"$PY" "$PACK_DIR/agente/memoria_md.py" --dest "$CLAUDE_HOME/memoria" --repo "$PACK_DIR/.." --claude-home "$CLAUDE_HOME" --scan >/dev/null \
  || warn "falha ao gerar a memória — rode: $PY $PACK_DIR/agente/memoria_md.py --dest $CLAUDE_HOME/memoria --scan"

"$PY" "$PACK_HOME/pack.py" stats || true
say "Video AI Pack instalado. Reinicie o Claude Code e teste:"
echo '   "decupa o video.mp4, colorgrade cinematic e legenda karaokê pra Reels"'

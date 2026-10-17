# Prompt para continuar no Claude Code local (Windows)

## 1. Abrir a sessão local com Remote Control (no seu PC)
No **PowerShell** (não precisa de admin):
```powershell
# se ainda não tem o Claude Code:
irm https://claude.ai/install.ps1 | iex
# baixar o projeto (branch com o pack, até o PR #1 ser mesclado):
git clone -b claude/video-editing-plugins-research-973wsr https://github.com/clebercantos/gestao.git $env:USERPROFILE\gestao
cd $env:USERPROFILE\gestao
claude            # faça o login na primeira vez e depois saia com /exit
claude remote-control
```
A sessão aparece no app do Claude (celular/web) e roda **no seu computador**. Cole nela o prompt abaixo.

## 2. Prompt (copie tudo entre as linhas)

---
Você está rodando LOCALMENTE no meu Windows, na pasta do repositório `gestao`. Continue o trabalho da sessão na nuvem de 2026-10-17.

1. Leia `CLAUDE.md`, `memoria/memoria.md`, `memoria/INDEX.md` e `memoria/historico/2026-10-17_video-ai-pack.md` para recuperar o contexto. Siga as preferências e decisões registradas lá.
2. Confira os pré-requisitos (`git`, `py`, `node`, `ffmpeg`, `claude`) e me mostre o que falta.
3. Pergunte só uma vez quais apps eu tenho instalados (Premiere, After Effects, Resolve) e quais MCPs ativar. Depois rode, pela pasta `video-ai-pack\agente`:
   `powershell -ExecutionPolicy Bypass -File .\instalar-agente.ps1 -Apps <apps> -Mcp <mcps>`
   Acompanhe a saída e corrija os erros que aparecerem, editando os scripts do repositório se for bug.
4. Verifique a instalação:
   - `powershell -File video-ai-pack\agente\agente.ps1 -Modo status` e o relatório `%LOCALAPPDATA%\VideoAIAgent\relatorios\ultimo.md`;
   - `Get-ScheduledTask -TaskPath \VideoAIAgent\` (3 tarefas);
   - `~/.claude/settings.json` com os hooks `video_intent.py`, `memoria_hook.py` e `registrar_conversa.py`;
   - `~/.claude/memoria/` com `memoria.md`, `INDEX.md`, `skills.md`, `mcps.md` e `agentes.md`.
5. Teste o fluxo de vídeo: gere um clipe de teste com ffmpeg (ou use um vídeo que eu indicar) e rode decupagem, colorgrade e legendas pelos scripts de `video-ai-pack\skills\*\scripts`. Mostre o frame `antes_depois.png`.
6. Liste o que só eu posso fazer (login `/mcp` dos conectores, painel CEP do Premiere, preferência de scripts do After Effects) e me guie passo a passo.
7. Registre em `~/.claude/memoria/memoria.md` o que aprender: correções, caminhos reais do meu PC, versões dos apps. Corrija bugs encontrados nos arquivos do repositório; faça commit e push na branch `claude/video-editing-plugins-research-973wsr`.
8. No final, me dê um resumo curto: o que está funcionando, o que falhou e o próximo passo.
---

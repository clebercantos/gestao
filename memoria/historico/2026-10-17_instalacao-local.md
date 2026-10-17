# Conversa 2026-10-17 — Instalação local no Windows e correções

Sessão Claude Code local · branch `claude/video-editing-plugins-research-973wsr`. Continuação de [video-ai-pack](2026-10-17_video-ai-pack.md).

## Feito
- Pré-requisitos conferidos (git, py, node, ffmpeg, claude); pack, hooks, memória e 3 tarefas agendadas já estavam instalados.
- Teste de ponta a ponta com clipe sintético (vídeo + fala TTS): decupagem, colorgrade e legendas passam.
- DaVinci Resolve MCP trocado pelo projeto samuelgursky (`npx davinci-resolve-mcp setup`); conectou no Resolve Studio.
- GitHub CLI instalado e autenticado; commits enviados.

## Bugs corrigidos
- faster-whisper quebrava com `av`>=17: áudio agora decodificado via ffmpeg.
- Whisper em "auto" escolhia CUDA sem cublas: padrão CPU (`VIDEO_WHISPER_DEVICE`).
- ffmpeg 9 removeu `-filter_complex_script`: grafo inline.
- Texto repetido em trechos da decupagem: agora usa as palavras de cada trecho.
- JSON/SRT gravados em cp1252 no Windows: tudo UTF-8 explícito.
- Roteador: "exporta pro Reels" não puxa mais skill de conteúdo social.
- Instaladores `.ps1` com BOM; instalador do Resolve usa o pacote correto.

## Pendências (só o usuário)
- [ ] Premiere: painel MCP Bridge "Running" (um único painel CEP).
- [ ] After Effects: abrir sem `-m` e permitir scripts em rede/arquivos.
- [ ] `/mcp`: autenticar o conector Adobe; reiniciar o app do Claude para o Resolve aparecer.
- [ ] Teste da primeira sessão no Premiere/AE depois que estiverem abertos.
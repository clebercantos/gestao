# Video AI Pack — prompt completo, o que foi feito e o que falta

> Trevisa Films · gerado em 2026-10-17 · repositório `clebercantos/gestao` (**público**: aqui não entram senhas, e-mails nem dados de clientes).
> Uso: cole a **Parte 1** numa conversa nova do Claude, do Claude Code local ou da nuvem para retomar tudo com o contexto completo. As outras partes são a referência.

---

## Parte 1 — Prompt para colar numa sessão nova

```text
Você é o editor-chefe e mantenedor do "Video AI Pack" da Trevisa Films. Responda sempre em português do Brasil.

CONTEXTO
- Eu edito vídeo (Premiere, After Effects, DaVinci Resolve, motion, colorgrade, decupagem, legendas) no Windows.
  Fuso America/Sao_Paulo (UTC−3). Reinícios do Claude só depois de 01:20 da manhã.
- Quero tudo automático e autônomo: aprimorar o prompt, escolher a ferramenta, executar e fazer manutenção sem eu pedir.
- Repositório: github.com/clebercantos/gestao (PÚBLICO). No PC: %USERPROFILE%\gestao.
  Memória privada no PC: ~/.claude/memoria/ (fonte da verdade). Memória pública: gestao/memoria/.

ANTES DE RESPONDER
1. Leia memoria/memoria.md e memoria/INDEX.md. Antes de pesquisar fora, consulte skills.md, mcps.md, agentes.md e historico/.
   No PC, prefira ~/.claude/memoria/.
2. Leia PROMPT-COMPLETO.md (este arquivo), seções "O que falta", para saber onde paramos.

REGRAS
- Correção, preferência nova ou aprendizado: 1 linha datada em memoria.md, na seção certa. Diga o que salvou.
  O que for privado vai só para ~/.claude/memoria/.
- Posso instalar/configurar MCPs, CLIs e pacotes no PC e usar o PC para validar as configurações sem perguntar.
  Avisar ANTES de: gastar créditos pagos (> ~US$ 5), publicar, force-push, apagar mídia ou dados do usuário.
- Nunca sobrescrever mídia original. Sempre manter um projeto editável (EDL/XML + LUT).
- Rota de vídeo: MCP do app aberto > conector na nuvem > scripts ffmpeg locais do pack.
  No projeto gestao do PC, a rota principal para Premiere/AE/Resolve é o magnific-plugins
  (reserva: premiere-pro, aftereffects, davinci-resolve). Filmit, Adobe, Canva e Google estão desativados nesse projeto.
- Para lote ou "faz tudo": use video-ai-pack/tools/pipeline.ps1 (sem gastar tokens) e depois revise o decisoes.md.
- Todo pedido de vídeo segue a skill video-orquestrador: Brief → Inventário → Rota → Execução → Registro.
- Ao terminar uma conversa importante: resumo sem dados sensíveis em memoria/historico/AAAA-MM-DD_<tema>.md.

AGORA
Continue a partir da lista "O que falta" deste arquivo. Primeiro, diga em 3 linhas o estado atual. Depois, faça tudo o que não depende de mim.
```

---

## Parte 2 — O que foi construído

### 2.1 Estrutura do repositório

| Caminho | O que é |
|---|---|
| `CLAUDE.md` | Instruções do repositório. Importa `memoria/memoria.md` e `memoria/INDEX.md`. |
| `PROMPT-LOCAL.md` | Como abrir a sessão local com Remote Control e o prompt de instalação. |
| `PROMPT-COMPLETO.md` | Este arquivo. |
| `memoria/` | Memória pública: `memoria.md`, `INDEX.md`, `skills.md`, `mcps.md`, `agentes.md`, `contas.json`, `instrucoes-claude-ai.md`, `historico/`. |
| `video-ai-pack/skills/` | As 7 skills próprias (veja 2.2). |
| `video-ai-pack/hooks/` | `video_intent.py`, `memoria_hook.py`, `registrar_conversa.py`. |
| `video-ai-pack/tools/pack.py` | Roteador de skills: `route`, `sync`, `list`, `install`, `config`, `stats`. |
| `video-ai-pack/tools/pipeline.py` + `pipeline.ps1` | Pipeline de um comando, com pasta monitorada opcional. |
| `video-ai-pack/catalogo/` | `CATALOGO.md` + `skills.json`: o top 100 da comunidade com notas. |
| `video-ai-pack/agente/` | Agente Windows: `agente.py`, `agente.ps1`, `instalar-agente.ps1`, `memoria_md.py` e o subagente `video-ai-mantenedor.md`. |
| `video-ai-pack/prompts/biblioteca.md` | Biblioteca de prompts de edição. |
| `video-ai-pack/install.ps1` / `install.sh` | Instaladores para Windows e para macOS/Linux/WSL. |
| `video-ai-pack/config/` | Trecho do CLAUDE.md e exemplo de `claude_desktop_config.json`. |

### 2.2 As 7 skills próprias (sempre instaladas em `~/.claude/skills/`)

| Skill | Faz | Script |
|---|---|---|
| `video-orquestrador` | Porta de entrada de qualquer pedido de vídeo. Segue 5 fases: Brief (aprimora o prompt), Inventário, Rota, Execução e Registro. | — |
| `video-decupagem` | Corta silêncios (−35 dB em estúdio, −30 dB em externa), fillers PT-BR e takes repetidos; transcreve com faster-whisper e gera EDL. | `decupagem.py` |
| `video-colorgrade` | Analisa a cor (balanço de branco gray-world antes dos níveis), aplica os looks cinematic, natural, quente, frio, pb e vintage e gera uma LUT `.cube`. | `analisar_cor.py` |
| `video-audio` | Redução de ruído proporcional ao piso, EQ e compressão de voz, loudness por plataforma (web −14, TV −23, podcast −16 LUFS, TP −1) e ducking da trilha. | `audio.py` |
| `video-legendas` | SRT PT-BR (42 car./linha, 17 CPS) e karaokê vertical gravado no vídeo. | `legendas.py` |
| `video-motion` | Lower thirds, títulos e animação no AE/Remotion/Lottie. | — |
| `video-entrega` | Exportação por plataforma e QA com ffprobe. | — |

### 2.3 Top 100 skills da comunidade (cofre + roteador)

- Foram cruzadas **5.490** skills (skills.sh + claudemarketplaces). Ficaram 697 relevantes, 105 passaram pela curadoria e **100** entraram no ranking.
  Pesos: comunidade 30, aderência 35, segurança 15, tokens 15, frescor 5.
- Instalar as 100 custaria ~10,2k tokens fixos por sessão. Por isso elas ficam num **cofre** (`~/.claude/video-ai-pack/vault`), e o roteador carrega **2 a 5 por pedido, dentro de 7k tokens**.
- Exemplo: "reels com legenda, cor cinematográfica e áudio limpo" escolhe `color-grading-finishing`, `auto-editor-transcribe`, `workflow-podcast-pipeline`, `reel-export` e `skill-captions` (≈ 6,98k tokens).
- Teste manual: `py -3.12 ~/.claude/video-ai-pack/pack.py route "<pedido>"`.
- Skills da conta claude.ai que também servem: `anthropic-skills:motion-design` (LottieFiles), `gsap-*` (GreenSock), `threejs-*`, além das skills `adobe-for-creativity:*` (quick cut, resize, social variations).

### 2.4 MCPs e conectores

| Nome | Onde | Uso / estado |
|---|---|---|
| `magnific-plugins` (magnific-local-mcp) | PC, projeto gestao | **Rota principal**: lê e edita Premiere/AE/Resolve pelo painel Magnific (`premiere_project_info`, `after_effects_project_info`, `local_status`…). Exige o painel ligado dentro do app. |
| `premiere-pro` | PC | `npx -y premiere-pro-mcp@latest` + painel CEP. Testado: projeto, import, sequência, split, in/out, export H.264. Não aplica LUT `.cube`. |
| `aftereffects` | PC | `npx -y @kumoproductions/mcp-aftereffects@latest`. Testado: comp, keyframes, render Lossless (`.mp4` exige o AME). |
| `davinci-resolve` | PC | `npx davinci-resolve-mcp setup` (samuelgursky; o pacote do PyPI é outro projeto). Exige External scripting = Local. Testado: projeto, import, timeline. |
| `opusclip` | PC (OAuth) | Conectado. Clipes virais, legendas, reframe. |
| Claude Docs | PC e nuvem | Documentos compartilháveis. |
| Filmit | conta claude.ai | AE, Premiere (`pr_*`) e Resolve (`dv_*`). Plano free com 50 ações/dia; o painel nunca foi conectado. Desativado no gestao. |
| Magnific (nuvem) | conta claude.ai | Cor, corte, upscale e áudio por IA (consome créditos). Desativado no gestao. |
| Adobe for creativity | conta claude.ai | Quick cut, resize, melhorar fala, fontes, PDF. O nome mudou para "claude.ai Adobe"; desativado no gestao. |
| Canva, Gmail, Drive, Calendar, AEM, Adobe Marketing Agent | conta claude.ai | Desativados no gestao; seguem ativos nas outras pastas. |
| invideo, higgsfield | opcionais (OAuth) | Não instalados. `install.ps1 -Mcp invideo,higgsfield`. |

O isolamento por projeto fica em `~/.claude.json` → `projects["C:/Users/<usuario>/gestao"].disabledMcpServers` (19 itens + "claude.ai Adobe") e em `gestao\.claude\settings.local.json` (plugin hyperframes desligado). Há um backup em `~/.claude.json.bak_20261017`.

### 2.5 Agentes, hooks e automações

**Hooks** (`~/.claude/settings.json`, rodam com o Python 3.12):

| Evento | Script | Faz |
|---|---|---|
| UserPromptSubmit | `video_intent.py` | Detecta pedido de vídeo e injeta as skills certas (roteador com orçamento de tokens). |
| UserPromptSubmit | `memoria_hook.py` | Detecta correção, preferência, "lembre disso" e "📌 Para a memória:" e manda gravar em `memoria.md`. |
| SessionEnd | `registrar_conversa.py` | Salva o resumo da conversa em `~/.claude/memoria/conversas/`, mascarando segredos. |

**Video AI Agent**: Agendador de Tarefas `\VideoAIAgent\`, dados em `%LOCALAPPDATA%\VideoAIAgent\`.

| Tarefa | Quando | Faz |
|---|---|---|
| Saude | logon +5 min e a cada 6 h | Confere 28 itens e repara sozinha (`--reparar`). |
| Manutencao | diária às 03:17 | Atualiza pack, cofre e pacotes; regenera `skills.md`, `mcps.md` e `agentes.md`; sincroniza a memória; segue a `main` quando a branch do PR some. |
| Descoberta | segunda às 09:13 | Monitora skills, MCPs e releases e faz a pesquisa da semana com `claude -p`. Adota até 3 skills auditadas (nota ≥ 70); MCPs novos ela só reporta. |
| Pipeline (opcional) | a cada 10 min | Só existe se você registrar com `pipeline.ps1 -Pasta X -Registrar`. |

Um lock impede execuções simultâneas: a segunda espera até 45 min e sai com código 0. Para rodar à mão: `powershell -File agente.ps1 -Modo status|saude|manutencao|descoberta|memoria|tudo`.

**Subagente do Claude Code**: `video-ai-mantenedor`, que verifica a saúde, repara, atualiza e revisa as descobertas.

**Sessões Claude**:

| Sessão | Papel |
|---|---|
| Sessão na nuvem (claude.ai/code) | Pesquisa, código, PRs, acompanhamento de PR e check-ins agendados. |
| Sessão local `desktop-ve4abku-tidy-ullman` | Roda no PC via `claude remote-control`. Instala, testa os apps e valida. Está no modo "Aceitar edições", então pede aprovação para comandos do PowerShell. |

As duas conversam por `send_message`.

### 2.6 Memória permanente

- `memoria.md` é lido em toda conversa via `CLAUDE.md`, tanto no PC quanto na nuvem. Para o claude.ai web, cole `memoria/instrucoes-claude-ai.md` no perfil ou no projeto.
- `skills.md`, `mcps.md` e `agentes.md` são regenerados todo dia pelo agente (`memoria_md.py`).
- `historico/` guarda os resumos curados. `conversas/` existe só no PC e é privada.

### 2.7 Pipeline de um comando

```powershell
cd $env:USERPROFILE\.claude\video-ai-pack\tools     # ou gestao\video-ai-pack\tools
.\pipeline.ps1 -Video D:\bruto\entrevista.mp4 -Preset reels      # reels | youtube | tv | podcast
.\pipeline.ps1 -Video ... -Preset youtube -Look cinematic -Trilha musica.mp3
.\pipeline.ps1 -Pasta D:\VideoAI -Registrar -Preset reels        # vigia D:\VideoAI\entrada a cada 10 min
.\pipeline.ps1 -Remover                                          # desliga a vigilância
```

As etapas são decupagem → cor → áudio → formato (9:16 no reels) → legendas → `ENTREGA\`. A pasta de entrega recebe o vídeo, `cortes.edl`, `grade.cube` e `legendas.srt`, e o `decisoes.md` registra as escolhas.

---

## Parte 3 — Linha do tempo (2026-10-17)

1. Pesquisei as 2 últimas semanas de plugins, skills e MCPs de vídeo e construí o pack: 6 skills, hook de intenção, instaladores e biblioteca de prompts.
2. Ranqueei o top 100 de skills com dados da comunidade e criei o cofre + roteador com orçamento de tokens.
3. Criei o agente Windows (saúde, manutenção, descoberta) e o instalador dele.
4. Montei o sistema de memória: `memoria.md`, os MDs de skills, MCPs e agentes, o histórico e os hooks de memória e de conversas.
5. Abri a sessão local com Remote Control e instalei tudo no PC.
6. Testei os apps abertos: Premiere OK (exceto LUT), AE OK, Resolve OK e saúde 28/28. Corrigi Python 3.12, `av`>=17, CUDA, ffmpeg 9, BOM/cp1252 e o MCP do Resolve.
7. **PR #1 mesclado**: o pack base.
8. **PR #2 mesclado** (merge 239b704): skill `video-audio`, `pipeline.py`/`.ps1`, fallback de branch do agente, lock com espera, instruções para o claude.ai e o fuso horário na memória. O pipeline foi validado no Windows: reels 1080x1920 com karaokê, 39,7 s → 20 s e −14,4 LUFS; youtube 1920x1080 com SRT.
9. O usuário isolou os MCPs no projeto gestao, com o magnific-plugins como rota principal.
10. Validação completa após o merge: saúde 28/28, 7 skills, 3 tarefas com código 0, lock OK, hooks OK, memória OK e 7 MCPs conectados. Corrigi o instalador, que não copiava o `pipeline.*`.
11. **PR #3 aberto**: correção dos instaladores e memória da validação.

---

## Parte 4 — O que falta

### Depende de você

- [ ] **Mesclar o PR #3**: https://github.com/clebercantos/gestao/pull/3. Depois, rode no PC:
  `cd $env:USERPROFILE\gestao; git pull origin main; powershell -ExecutionPolicy Bypass -File video-ai-pack\install.ps1 -SkipPip -NoSync`
- [ ] **Abrir os apps para o teste final dos MCPs**:
  - Premiere com o painel Magnific ligado;
  - After Effects;
  - DaVinci Resolve, com Preferences > General > External scripting = Local.
- [ ] **Trocar a sessão local para o modo Auto** no seletor ao lado da caixa de mensagem (ou Shift+Tab no terminal). Assim ela roda sem pedir aprovação de cada comando. Enquanto isso, aprove os pedidos do PowerShell no app.
- [ ] **Depois de 01:20**: reiniciar o app do Claude e rodar de novo, na pasta gestao, `claude remote-control`. A lista de ferramentas do projeto isolado só encolhe numa sessão nova.
- [ ] **Colar `memoria/instrucoes-claude-ai.md`** no perfil ou num projeto do claude.ai, para as conversas web lerem a memória.
- [ ] Opcional: escolher uma pasta para o pipeline vigiar (`pipeline.ps1 -Pasta X -Registrar`).
- [ ] Opcional: apagar a branch `claude/install-pipeline-fix` no GitHub. Ela já foi incorporada ao PR #3.
- [ ] Opcional: repositório privado para a memória (`instalar-agente.ps1 -RepoMemoria <url>`).
- [ ] Opcional: Filmit (painel no app → aba MCP → Connect), se quiser reativá-lo no gestao.
- [ ] Opcional: a cota de revisão do Codex no GitHub está esgotada. O revisor automático volta quando ela renovar.

### Feito pelos agentes, quando você liberar

- [ ] Com os apps abertos: 1 leitura e 1 edição num projeto temporário em cada app (magnific-plugins e o MCP de reserva), incluindo aplicar o `grade.cube` do pipeline no Resolve. Depois apagar os temporários.
- [ ] Conferir a primeira Descoberta real (segunda às 09:13) e o relatório em `%LOCALAPPDATA%\VideoAIAgent\relatorios\ultimo.md`.
- [ ] Conferir que `~/.claude/memoria/conversas/` continua recebendo as sessões e que a Manutenção das 03:17 regenera os MDs.
- [ ] Gravar na memória o resultado dos testes dos apps e fechar as pendências do histórico.

---

## Parte 5 — Comandos úteis (PowerShell)

```powershell
# estado geral e reparo
powershell -File $env:USERPROFILE\gestao\video-ai-pack\agente\agente.ps1 -Modo status
powershell -File $env:USERPROFILE\gestao\video-ai-pack\agente\agente.ps1 -Modo saude
Get-ScheduledTask -TaskPath \VideoAIAgent\ | Get-ScheduledTaskInfo | select TaskName,LastTaskResult,NextRunTime

# reinstalar/atualizar o pack (sem pip, sem sincronizar o cofre)
cd $env:USERPROFILE\gestao; git pull origin main
powershell -ExecutionPolicy Bypass -File video-ai-pack\install.ps1 -SkipPip -NoSync

# roteador de skills
py -3.12 $env:USERPROFILE\.claude\video-ai-pack\pack.py route "decupa e legenda pra reels"
py -3.12 $env:USERPROFILE\.claude\video-ai-pack\pack.py stats

# MCPs do projeto
cd $env:USERPROFILE\gestao; claude mcp list

# sessão local acessível pelo app
cd $env:USERPROFILE\gestao; claude remote-control
```

## Parte 6 — Aprendizados técnicos que não podem se perder

O registro completo está em `memoria/memoria.md`. Os principais:

- **Python e transcrição:**
  - faster-whisper só funciona no **Python 3.12** do PC; o padrão do `py` é 3.15.
  - O áudio é decodificado com ffmpeg porque `av`>=17 quebra o faster-whisper.
  - A transcrição roda na CPU por padrão; `VIDEO_WHISPER_DEVICE=cuda` liga a GPU.
- **ffmpeg 9** removeu `-filter_complex_script`.
- **Windows:**
  - `.ps1` com acento precisa de BOM; JSON não pode ter.
  - Use `py` em vez de `python`.
  - Com `-File`, listas chegam como uma string só e precisam de `-split ','`.
  - Arquivos gravados por Python precisam de `encoding="utf-8"`.
- **Apps:**
  - O MCP do Premiere não aplica LUT `.cube`: use Lumetri > Creative > Look, ou o Resolve.
  - O AE só exporta `.mp4` com o AME.
  - O Resolve exige External scripting = Local.
- **Skills:**
  - Os números de instalação do skills.sh são inflados por packs e espelhos.
  - "caption" geralmente é legenda de post, não de vídeo.
- **Sessões e repositório:**
  - Sessões na nuvem não acessam o PC: é preciso o Claude Desktop ou `claude remote-control`.
  - O repositório é público: nada privado nele.

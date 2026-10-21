# Agentes, hooks e automações

Atualizado em 2026-10-19 · fonte: documentação do repositório (sem varredura local).

## Video AI Agent (Windows, Agendador de Tarefas `\VideoAIAgent\`)

| Rotina | Quando | Faz |
|---|---|---|
| Saude | logon +5 min e a cada 6 h | confere 20 itens e repara sozinho |
| Manutencao | diária 03:17 | atualiza pack/cofre/pacotes/sistema, regenera estes MDs, sincroniza memória privada |
| Descoberta | segunda 09:13 | monitora skills/MCPs/releases + pesquisa web via `claude -p`; adota até 3 skills auditadas |
| Pipeline (opcional) | a cada 10 min, se registrado com `pipeline.ps1 -Registrar` | processa vídeos soltos na pasta `entrada` e gera ENTREGA |

- Código: `video-ai-pack/agente/` (`agente.py`, `agente.ps1`, `instalar-agente.ps1`)
- Dados: `%LOCALAPPDATA%\VideoAIAgent\` (`config.json`, `relatorios\ultimo.md`, `logs\`, `estado\`)
- Manual: `powershell -File agente.ps1 -Modo status|saude|manutencao|descoberta|tudo`

## Subagentes do Claude Code

| Agente | Para quê |
|---|---|
| `video-ai-mantenedor` | Mantenedor do Video AI Pack e do Video AI Agent no Windows. Use para checar a saúde da instalação de IA para vídeo, reparar, atualizar, ver relatórios, revisar skills/MCPs novos descobertos e aprovar… |

## Hooks instalados (`~/.claude/settings.json`)

| Evento | Script | Faz |
|---|---|---|
| UserPromptSubmit | `video_intent.py` | detecta pedido de vídeo e injeta as skills certas (roteador, orçamento de tokens) |
| UserPromptSubmit | `memoria_hook.py` | detecta correção/preferência/"lembre disso" e manda registrar em `memoria.md` |
| SessionEnd | `registrar_conversa.py` | salva o resumo de cada conversa em `~/.claude/memoria/conversas/` (privado) |

## Automações na nuvem (sessões claude.ai/code)

- Sessões que abrem PR acompanham os eventos dele (CI, revisões) até o merge.
- Sessões na nuvem leem `CLAUDE.md` e `memoria/` do repositório (versão pública da memória).

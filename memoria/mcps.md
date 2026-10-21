# MCPs e conectores — referência completa

Atualizado em 2026-10-19 · fonte: documentação do repositório (sem varredura local).

## Conectores da conta claude.ai

| Conector | Uso | Status |
|---|---|---|
| Filmit | controla os apps locais: After Effects (comps, camadas, keyframes, expressões), Premiere (pr_*: timeline, cortes, efeitos, legendas, markers), DaVinci Resolve … | conectado na conta (plano free, 50 ações/dia); falta ligar o painel Filmit no AE/Premiere → aba MCP → Connect |
| Adobe for creativity | Photoshop/Lightroom/Premiere/Express/Firefly/Acrobat na nuvem: video_create_quick_cut, video_resize, media_enhance_speech, media_summarize, fontes, PDF, imagem | conectado; a versão plugin pede autorização em Settings → Connectors |
| Magnific | vídeo/imagem/áudio por IA: video_color_grade, video_color_transfer, video_magic_cut, video_upscale, video_hdr, audio_clean_speech, brand kits | conectado (consome créditos) |
| Canva | designs, brand kits, import de motion do Claude, exportação | conectado |
| Adobe Experience Manager | conteúdo AEM (sites, fragments) | conectado |
| Adobe Marketing Agent | agente de marketing Adobe | conectado |
| Claude Docs | documentos vivos compartilháveis | conectado |
| Gmail | e-mail | conectado |
| Google Calendar | agenda | conectado |
| Google Drive | arquivos | conectado |
| GitHub | repositório clebercantos/gestao (sessões Claude Code na nuvem) | conectado |

## MCPs do Video AI Pack

| Nome | Tipo | Comando / URL | Observações |
|---|---|---|---|
| `premiere-pro` | local (CEP/UXP) | `npx -y premiere-pro-mcp@latest` | rodar `npx -y premiere-pro-mcp@latest --install-cep` e abrir Window > Extensions > MCP for Adobe Premiere Pro ([fonte](https://github.com/leancoderkavy/premiere-pro-mcp)) |
| `aftereffects` | local | `npx -y @kumoproductions/mcp-aftereffects@latest` | AE: Preferences > Scripting & Expressions > Allow Scripts to Write Files and Access Network; Node 24+ ([fonte](https://github.com/kumoproductions/mcp-aftereffects)) |
| `davinci-resolve` | local (venv em %LOCALAPPDATA%) | `npx -y davinci-resolve-mcp setup → venv\Scripts\python.exe src\server.py` | samuelgursky; o pacote PyPI de mesmo nome é outro projeto e quebra com mcp 2.x. Resolve: Preferences > General > External scripting = Local ([fonte](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-session)) |
| `opusclip` | remoto (OAuth) | `https://mcp.opus.pro/mcp` | clipes virais, legendas, reframe, agendamento ([fonte](https://www.opus.pro/mcp)) |
| `invideo` | remoto (OAuth) | `https://mcp.invideo.io/mcp` | timeline, cor, mix, legendas, exporta para Premiere/FCP/Resolve ([fonte](https://invideo.io/mcp/)) |
| `higgsfield` | remoto (OAuth, pago) | `https://mcp.higgsfield.ai/mcp` | Katana: motion editável no After Effects ([fonte](https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-claude)) |

Instalar/atualizar: `install.ps1 -Mcp premiere,ae,resolve,opusclip,invideo,higgsfield` (ou `all`). Remotos: login em `/mcp`.

## Alternativas pesquisadas (não instaladas)

- [DaVinci Resolve 21.1 (oficial Blackmagic)](https://www.cgchannel.com/2026/09/blackmagic-design-releases-resolve-21-1/)
- [barckley75/resolve-claude-mcp](https://github.com/barckley75/resolve-claude-mcp)
- [samuelgursky/davinci-resolve-mcp (+10 skills)](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-session)
- [hetpatel-11/Adobe_Premiere_Pro_MCP](https://github.com/hetpatel-11/adobe_premiere_pro_mcp)
- [antipaster/Adobe-Premiere-Pro-MCP (170+ ferramentas)](https://github.com/antipaster/adobe-premiere-pro-mcp)
- [TheLlamainator/after-effects-mcp](https://github.com/LobzyJay/motion-design-with-claude)
- [JUNKDOGE-JOE/after-effects-mcp](https://github.com/JUNKDOGE-JOE/after-effects-mcp)
- [Synthetic AE MCP (270+ ferramentas)](https://synthetic.com.ar/ae-mcp)
- [OpenClip MCP](https://openclip.app/mcp)
- [Palmier Pro (editor macOS com MCP)](https://explainx.ai/blog/palmier-pro-ai-video-editor-mcp-claude-guide-2026)

Regra: numa sessão, o agente instala MCPs novos sem pedir (decisão em `memoria.md`); a Descoberta agendada só reporta.

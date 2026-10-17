# Biblioteca de prompts — Video AI Pack

Com o pack instalado, você pode escrever pedidos curtos: o hook detecta a intenção e o
`video-orquestrador` expande tudo num Brief de Edição. Os modelos abaixo servem quando
você quer controle fino. Troque o que está entre `< >`.

## 1. Pipeline completo (um comando)
```
Edite <arquivo.mp4> para <Reels | YouTube | LinkedIn>.
Objetivo: <ex.: gerar leads para curso de fotografia>. Tom: <dinâmico | clean | cinematográfico>.
Faça decupagem (silêncios, fillers, retakes), escolha os melhores <45> segundos com gancho forte,
colorgrade <cinematic | natural | quente>, legenda <karaokê | padrão> em PT-BR, lower third com
<nome/cargo>, trilha a −20 dB sob a voz, voz a −14 LUFS. Entregue MP4 + EDL + SRT + decisoes.md.
```

## 2. Decupagem de material bruto (várias câmeras/entrevistas)
```
Decupe a pasta <pasta/>: para cada clipe, tipo de plano, qualidade técnica, sonoras com TC e nota 1–5,
b-rolls úteis e descartes com motivo. No fim, proponha uma estrutura (gancho → contexto → valor → CTA)
com os TCs escolhidos e gere a timeline (EDL) do rough cut de <3 min>.
```

## 3. Premiere (com o MCP aberto)
```
No Premiere, duplique a sequência <nome> como _ORIGINAL, remova silêncios > 0,4 s com 3 frames de respiro,
adicione punch-in de 115% a cada mudança de assunto, crie a faixa de legendas a partir do SRT gerado e
aplique o grade.cube num adjustment layer. Exporte H.264 1080p para YouTube e valide o arquivo.
```

## 4. DaVinci Resolve — cor
```
No Resolve, na timeline <nome>: monte a árvore de nós 01_CST (<S-Log3/S-Gamut3.Cine> → Rec.709),
02_WB, 03_EXPO, 04_MATCH, 05_LOOK, 06_GRAIN. Faça shot match entre as câmeras A e B usando a A como referência,
look <teal&orange suave>, pele no skin line. Gere stills antes/depois de 3 planos para eu revisar.
```

## 5. After Effects — motion
```
No After Effects, crie uma comp 1920×1080 25 fps de 6 s: lower third com <Nome> / <Cargo>,
barra que entra com easeOutExpo em 14 frames, texto com stagger de 3 frames por palavra, saída espelhada
aos 5 s. Fontes da marca <Fonte>, cores <#HEX>. Renderize os frames 10, 40 e 140 para revisão.
```

## 6. Vertical a partir de horizontal
```
Transforme <video_16x9.mp4> em 3 cortes verticais de 30–45 s com os momentos mais fortes,
reenquadrando no rosto de quem fala, legenda karaokê amarela, gancho em texto nos 2 primeiros segundos
e CTA no final. Nomeie PROJETO_REELS_v001_<data>.mp4.
```

## 7. Correção técnica rápida
```
<arquivo> está escuro e azulado. Corrija exposição e balanço de branco sem look criativo,
mostre o antes/depois e me dê a LUT .cube para eu usar no Premiere.
```

## 8. Legendas com glossário
```
Legende <arquivo> (padrão, 2 linhas, 42 caracteres). Termos que devem sair exatamente assim:
<Lumetri, DaVinci, Trevisa Films, Sony FX3>. Entregue SRT, VTT e versão queimada.
```

## Palavras de estilo que o orquestrador entende
`cinematográfico`, `dinâmico/viral`, `clean/corporativo`, `documental`, `vintage/film`, `quente`, `frio`, `P&B`,
`Hormozi/karaokê`, `minimal` — cada uma vira parâmetros concretos (ritmo de corte, curva, saturação, grão, estilo de legenda).

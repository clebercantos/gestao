#!/usr/bin/env python3
"""Análise de cor + correção técnica automática + look + exportação de LUT .cube.

Uso:
  analisar_cor.py VIDEO [--look natural|cinematic|quente|frio|pb|vintage]
                  [--lut ARQUIVO.cube] [--log] [--samples 8] [--out DIR] [--apply]

Saídas em DIR:
  cor.json          medições por amostra + médias + correções escolhidas
  filtro.txt        cadeia de filtros ffmpeg final
  grade.cube        LUT 33^3 com correção + look (importável no Premiere/Lumetri e Resolve)
  antes_depois.png  comparação de um frame
  graded.mp4        (com --apply) vídeo com o grade aplicado
"""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path

LOOKS = {
    "natural": "",
    "cinematic": "curves=m='0/0 0.25/0.21 0.5/0.5 0.75/0.79 1/1',"
                 "colorbalance=rs=-0.05:gs=0.0:bs=0.06:rh=0.05:gh=0.01:bh=-0.04,eq=saturation=0.95",
    "quente": "colorbalance=rm=0.05:gm=0.01:bm=-0.05:rh=0.03:bh=-0.03,eq=saturation=1.03",
    "frio": "colorbalance=rm=-0.04:bm=0.05:rs=-0.02:bs=0.04,eq=saturation=0.97",
    "pb": "hue=s=0,curves=m='0/0 0.25/0.2 0.5/0.5 0.75/0.8 1/1'",
    "vintage": "curves=preset=vintage,eq=saturation=0.85",
}
# Efeitos espaciais/temporais que não cabem numa LUT (aplicados só no render)
FINISH = {
    "cinematic": "noise=alls=5:allf=t",
    "vintage": "noise=alls=12:allf=t,vignette=PI/5",
}


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
                         capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    return float(info["format"]["duration"]), v


def sample_stats(path, t):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1",
                        "-vf", "scale=640:-2,signalstats,metadata=print", "-f", "null", "-"],
                       capture_output=True, text=True)
    stats = {}
    for k in ("YAVG", "YMIN", "YMAX", "YLOW", "YHIGH", "UAVG", "VAVG", "SATAVG"):
        m = re.search(rf"lavfi\.signalstats\.{k}=([\d.]+)", r.stderr)
        if m:
            stats[k] = float(m.group(1))
    return stats


def sample_rgb(path, t):
    """Média RGB dos pixels de meio-tom (base do balanço de branco gray-world)."""
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(path),
                          "-frames:v", "1", "-vf", "scale=96:54,format=rgb24", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    acc, n = [0.0, 0.0, 0.0], 0
    for i in range(0, len(raw) - 2, 3):
        r, g, b = raw[i], raw[i + 1], raw[i + 2]
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if 38 < y < 217:
            acc[0] += r; acc[1] += g; acc[2] += b; n += 1
    return [c / n for c in acc] if n else None


def decide(avg, rgb, is_log, full_range):
    lo, hi = (0, 255) if full_range else (16, 235)
    span = hi - lo
    filters, why = [], []
    # balanço de branco primeiro (antes de esticar níveis, que amplificaria o desvio)
    if rgb:
        ref = sum(rgb) / 3
        gains = [max(0.8, min(1.25, 1 + 0.85 * (ref / c - 1))) for c in rgb]
        if max(abs(g - 1) for g in gains) > 0.04:
            filters.append(f"colorchannelmixer=rr={gains[0]:.3f}:gg={gains[1]:.3f}:bb={gains[2]:.3f}")
            why.append("balanço de branco (gray-world em meios-tons): ganhos R/G/B = " + "/".join(f"{g:.2f}" for g in gains))
    if is_log:
        why.append("material LOG: expandindo contraste/saturação (prefira a LUT oficial da câmera via --lut)")
        filters.append("curves=m='0/0 0.18/0.08 0.5/0.5 0.82/0.92 1/1',eq=saturation=1.3")
        return filters, why
    # níveis: preto levantado / branco baixo
    ylow, yhigh = avg.get("YLOW", lo), avg.get("YHIGH", hi)
    imin, imax = 0.0, 1.0
    if ylow - lo > 12 or hi - yhigh > 15:
        # p10/p90 -> ~4%/~92%: estica sem esmagar sombras nem estourar altas
        imin = max(0.0, (ylow - lo) / span - 0.04)
        imax = min(1.0, (yhigh - lo) / span + 0.08)
        filters.append(f"colorlevels=rimin={imin:.3f}:gimin={imin:.3f}:bimin={imin:.3f}:rimax={imax:.3f}:gimax={imax:.3f}:bimax={imax:.3f}")
        why.append(f"níveis: esticando pretos/brancos (p10={ylow:.0f}, p90={yhigh:.0f})")
    # exposição (medida já depois dos níveis): média alvo 0.45 do range
    y = min(1.0, max(0.0, ((avg["YAVG"] - lo) / span - imin) / (imax - imin)))
    if y < 0.36 or y > 0.58:
        gamma = max(0.7, min(1.5, math.log(max(y, 0.02)) / math.log(0.45)))
        filters.append(f"eq=gamma={gamma:.2f}")
        why.append(f"exposição: Y médio {y:.2f} -> gamma {gamma:.2f}")
    return filters, why


def write_cube(chain, out_path, size=33):
    """Gera LUT .cube aplicando a cadeia a uma Hald CLUT identidade (nível 6 => 36^3) e reamostrando p/ 33^3."""
    level = 6
    n = level * level  # 36 pontos por eixo
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"haldclutsrc={level}",
                          "-frames:v", "1", "-vf", (chain + "," if chain else "") + "format=rgb24",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout

    def px(r, g, b):
        i = 3 * (r + g * n + b * n * n)
        return raw[i] / 255, raw[i + 1] / 255, raw[i + 2] / 255

    def interp(x, y, z):  # trilinear
        fx, fy, fz = x * (n - 1), y * (n - 1), z * (n - 1)
        x0, y0, z0 = int(fx), int(fy), int(fz)
        x1, y1, z1 = min(x0 + 1, n - 1), min(y0 + 1, n - 1), min(z0 + 1, n - 1)
        dx, dy, dz = fx - x0, fy - y0, fz - z0
        res = [0.0, 0.0, 0.0]
        for xi, wx in ((x0, 1 - dx), (x1, dx)):
            for yi, wy in ((y0, 1 - dy), (y1, dy)):
                for zi, wz in ((z0, 1 - dz), (z1, dz)):
                    w = wx * wy * wz
                    if w:
                        c = px(xi, yi, zi)
                        res = [res[k] + w * c[k] for k in range(3)]
        return res

    lines = ["TITLE \"Video AI Pack grade\"", f"LUT_3D_SIZE {size}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    for b in range(size):
        for g in range(size):
            for r in range(size):
                c = interp(r / (size - 1), g / (size - 1), b / (size - 1))
                lines.append(f"{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}")
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--look", default="natural", choices=sorted(LOOKS))
    ap.add_argument("--lut", help="LUT de câmera/criativa .cube aplicada antes do look")
    ap.add_argument("--log", action="store_true", help="força tratar como LOG")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--out")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    src = Path(a.video).resolve()
    out = Path(a.out or src.parent / f"{src.stem}_cor")
    out.mkdir(parents=True, exist_ok=True)
    dur, v = probe(src)
    full_range = v.get("color_range") == "pc"
    meta = json.dumps(v).lower() + src.name.lower()
    is_log = a.log or bool(re.search(r"s-?log|c-?log|v-?log|log-?c|f-?log|n-?log|braw", meta))
    hdr = v.get("color_transfer") in ("smpte2084", "arib-std-b67")

    times = [dur * (i + 0.5) / a.samples for i in range(a.samples)]
    samples = [dict(t=round(t, 2), **sample_stats(src, t)) for t in times]
    samples = [s for s in samples if "YAVG" in s]
    avg = {k: sum(s[k] for s in samples) / len(samples) for k in samples[0] if k != "t"}
    spread = max(s["YAVG"] for s in samples) - min(s["YAVG"] for s in samples)

    rgbs = [c for c in (sample_rgb(src, t) for t in times) if c]
    rgb = [sum(c[k] for c in rgbs) / len(rgbs) for k in range(3)] if rgbs else None
    tech, why = ([], ["LUT fornecida aplicada no lugar da correção técnica automática"]) if a.lut else decide(avg, rgb, is_log, full_range)
    chain = []
    if a.lut:
        chain.append(f"lut3d=file='{Path(a.lut).resolve()}'")
    chain += tech
    if LOOKS[a.look]:
        chain.append(LOOKS[a.look])
    lut_chain = ",".join(chain)
    render_chain = ",".join(c for c in (lut_chain, FINISH.get(a.look, "")) if c) or "null"

    write_cube(lut_chain, out / "grade.cube")
    (out / "filtro.txt").write_text(render_chain + "\n", encoding="utf-8")
    t_mid = times[len(times) // 2]
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t_mid:.2f}", "-i", str(src),
                    "-frames:v", "1", "-filter_complex",
                    f"[0:v]scale=960:-2,split[a][b];[b]{render_chain}[g];[a][g]hstack", str(out / "antes_depois.png")],
                   check=True)
    report = {"arquivo": src.name, "log": is_log, "hdr": hdr, "full_range": full_range, "look": a.look,
              "media": {k: round(x, 1) for k, x in avg.items()}, "variacao_luma_entre_amostras": round(spread, 1),
              "consistencia": "ok" if spread < 25 else "planos com exposição muito diferente: fazer shot match por plano",
              "decisoes": why, "filtro": render_chain, "amostras": samples}
    (out / "cor.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if a.apply:
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", render_chain,
                        "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "copy", str(out / "graded.mp4")],
                       check=True)
    print(json.dumps({k: report[k] for k in ("log", "hdr", "look", "decisoes", "consistencia")} | {"saida": str(out)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()

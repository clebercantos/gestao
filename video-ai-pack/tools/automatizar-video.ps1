#requires -Version 5.1
<#
.SYNOPSIS
  Inicia edicao automatizada local de video institucional sem sobrescrever originais.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\video-ai-pack\tools\automatizar-video.ps1
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\video-ai-pack\tools\automatizar-video.ps1 -Video "D:\Institucional.mp4" -DriveRemoto "gdrive:Trevisa/Revisao"
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\video-ai-pack\tools\automatizar-video.ps1 -Video "D:\Institucional.mp4" -Finalizar -UsarGPU
#>
[CmdletBinding()]
param(
    [string]$Video = "",
    [string]$PastaTrabalho = "",
    [switch]$Finalizar,
    [switch]$UsarGPU,
    [string]$DriveRemoto = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$toolDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agent = Join-Path $toolDir "edicao-aprovacao.py"
if (-not (Test-Path -LiteralPath $agent)) { throw "Script de edicao nao encontrado: $agent" }

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Comando ausente: $Name. Instale antes de usar esta automacao."
    }
}
Require-Command "py"
Require-Command "ffmpeg"
Require-Command "ffprobe"
& py -3.12 --version
if ($LASTEXITCODE -ne 0) { throw "Requer Python 3.12 (py -3.12)." }

if (-not $Video) {
    $dirs = @((Join-Path $env:USERPROFILE "Downloads"),
              (Join-Path $env:USERPROFILE "Videos"),
              (Get-Location).Path)
    $found = @($dirs | Where-Object { Test-Path -LiteralPath $_ } |
        ForEach-Object { Get-ChildItem -LiteralPath $_ -File -Filter "*.mp4" -ErrorAction SilentlyContinue } |
        Where-Object { $_.Name -like "*institucional*" } |
        Select-Object -ExpandProperty FullName -Unique)
    if ($found.Count -ne 1) {
        throw "Video institucional nao encontrado de forma unica em Downloads, Videos ou pasta atual. Informe -Video 'C:\Videos\institucional.mp4'."
    }
    $Video = $found[0]
}
$src = (Resolve-Path -LiteralPath $Video).Path
if (-not $PastaTrabalho) {
    $PastaTrabalho = Join-Path (Split-Path -Parent $src) ("REVISAO_" + [IO.Path]::GetFileNameWithoutExtension($src))
}
if (-not $Finalizar) {
    & py -3.12 -c "import numpy, faster_whisper"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Instalando as dependencias locais de transcricao no Python 3.12 ..."
        & py -3.12 -m pip install --user "numpy>=1.26,<3" "faster-whisper>=1.2,<2"
        if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar numpy/faster-whisper. Verifique o log acima." }
    }
}
$stage = if ($Finalizar) { "finalizar" } else { "preparar" }
$argsPython = @($agent, $stage, $src, "--trabalho", $PastaTrabalho)
if ($UsarGPU -and $Finalizar) { $argsPython += "--nvenc" }
Write-Host "Etapa: $stage. Arquivo original mantido intacto."
& py -3.12 @argsPython
if ($LASTEXITCODE -ne 0) { throw "A edicao falhou. O original nao foi sobrescrito." }

if ($DriveRemoto) {
    Require-Command "rclone"
    $remote = $DriveRemoto.TrimEnd("/", "\")
    # Só arquivos de revisão; não transfere o master confidencial por engano.
    if (-not $Finalizar) {
        foreach ($name in @("revisao.json", "transcricao.txt")) {
            $local = Join-Path $PastaTrabalho $name
            if (Test-Path -LiteralPath $local) {
                & rclone copyto $local ($remote + "/" + $name) --retries 2 --checkers 2 --transfers 1
                if ($LASTEXITCODE -ne 0) { throw "Falha ao enviar $name ao Google Drive via rclone." }
            }
        }
        $sample = Get-ChildItem -LiteralPath $PastaTrabalho -Filter "AMOSTRA_DA_EMENDA_*.mp4" -File |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($null -ne $sample) {
            & rclone copyto $sample.FullName ($remote + "/" + $sample.Name) --retries 2 --checkers 2 --transfers 1
            if ($LASTEXITCODE -ne 0) { throw "Falha ao enviar amostra ao Drive." }
        }
    } else {
        $final = Get-ChildItem -LiteralPath $PastaTrabalho -Filter "FINAL_4K_*.mp4" -File | Select-Object -First 1
        if ($null -eq $final) { throw "Arquivo 4K final nao encontrado para upload." }
        & rclone copyto $final.FullName ($remote + "/" + $final.Name) --retries 2 --checkers 2 --transfers 1
        if ($LASTEXITCODE -ne 0) { throw "Falha ao enviar a versão final ao Drive." }
    }
}
if ($Finalizar) {
    Write-Host "Exportacao 4K concluida. Confira QA_FINAL.json e escute a emenda antes de publicar."
} else {
    Write-Host "Previa preparada. Verifique AMOSTRA_DA_EMENDA.mp4 e PREVIA_COMPLETA_720p*.mp4."
    Write-Host "Para autorizar a exportacao, ajuste revisao.json: inicio, fim, aprovado=true."
    Write-Host "Em seguida execute o mesmo comando acrescentando -Finalizar."
}

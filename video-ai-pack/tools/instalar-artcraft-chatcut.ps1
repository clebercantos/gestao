# Integração oficial: ArtCraft + ChatCut (Windows)
# Fonte: https://github.com/storytold/artcraft
# Fonte: https://github.com/ChatCut-Inc/agent-plugin
# Este script é executado no PC Windows, não nos servidores do GitHub.
[CmdletBinding()]
param(
    [switch]$ArtCraft,
    [switch]$ChatCutClaude,
    [switch]$ChatCutCodex
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (-not ($ArtCraft -or $ChatCutClaude -or $ChatCutCodex)) {
    Write-Host "Escolha -ArtCraft, -ChatCutClaude e/ou -ChatCutCodex. Exemplo:"
    Write-Host "  .\instalar-artcraft-chatcut.ps1 -ArtCraft -ChatCutClaude -ChatCutCodex"
    exit 0
}
function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Comando '$Name' indisponível. Instale-o primeiro e execute novamente."
    }
}
function Assert-Success([string]$Label) {
    if ($LASTEXITCODE -ne 0) { throw "$Label falhou com código $LASTEXITCODE." }
}
if ($ArtCraft) {
    Write-Host "Consultando release oficial ArtCraft ..."
    $headers = @{ "User-Agent" = "Trevisa-Video-AI-Pack"; "Accept" = "application/vnd.github+json" }
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/storytold/artcraft/releases/latest" -Headers $headers
    $asset = @($release.assets | Where-Object { $_.name -match '^ArtCraft_.*_x64-setup\.exe$' } | Select-Object -First 1)
    if ($asset.Count -eq 0) { throw "Release sem instalador x64 Windows; consulte $($release.html_url)." }
    $downloadDir = Join-Path ([Environment]::GetFolderPath("UserProfile")) "Downloads"
    New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
    $dest = Join-Path $downloadDir $asset[0].name
    if (-not (Test-Path $dest)) {
        Invoke-WebRequest -Uri $asset[0].browser_download_url -OutFile $dest -UseBasicParsing
    }
    $signature = Get-AuthenticodeSignature -FilePath $dest
    Write-Host "Instalador: $dest"
    Write-Host "Assinatura: $($signature.Status)"
    Write-Host "SHA256: $((Get-FileHash -Path $dest -Algorithm SHA256).Hash)"
    if ($signature.Status -ne "Valid") {
        Write-Warning "Assinatura Authenticode não validada. Por segurança, não executarei o instalador automaticamente."
        Write-Host "Confira manualmente o release oficial: $($release.html_url)"
    } else {
        Start-Process -FilePath $dest -Wait
        Write-Host "Instalador executado. Confira o ArtCraft no menu Iniciar."
    }
}
if ($ChatCutClaude) {
    Require-Command git
    Require-Command claude
    Write-Host "Verificando plugin oficial ChatCut no Claude Code ..."
    & claude plugin marketplace add "https://github.com/ChatCut-Inc/agent-plugin.git"
    if ($LASTEXITCODE -ne 0) { Write-Warning "Marketplace talvez já exista. Conferindo estado atual." }
    & claude plugin marketplace list
    Assert-Success "Listar marketplaces"
    & claude plugin install "chatcut@chatcut-inc"
    if ($LASTEXITCODE -ne 0) {
        & claude plugin details "chatcut@chatcut-inc"
        Assert-Success "Instalar/validar plugin ChatCut"
    }
    Write-Host "Login OAuth interativo será aberto no navegador (se necessário)."
    & claude mcp login "plugin:chatcut:chatcut"
    Assert-Success "Autenticar ChatCut"
    & claude mcp get "plugin:chatcut:chatcut"
    Assert-Success "Verificar conexão ChatCut"
    Write-Host "Abra uma NOVA conversa no Claude Code para disponibilizar as ferramentas."
}
if ($ChatCutCodex) {
    Require-Command codex
    $url = "https://api.chatcut.io/api/external-mcp/mcp"
    & codex mcp get chatcut *> $null
    if ($LASTEXITCODE -ne 0) {
        & codex mcp add chatcut --url $url
        Assert-Success "Registrar MCP ChatCut no Codex"
    }
    Write-Host "Autenticando MCP ChatCut no Codex ..."
    & codex mcp login chatcut
    Assert-Success "Autenticar ChatCut no Codex"
    & codex mcp get chatcut
    Assert-Success "Verificar conexão ChatCut no Codex"
    Write-Host "Abra uma NOVA conversa no Codex para utilizar o MCP."
}
Write-Host "Concluído. Nenhum arquivo de mídia original foi alterado."

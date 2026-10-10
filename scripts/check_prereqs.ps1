# Pre-session check for Windows. Usage: powershell -ExecutionPolicy Bypass -File .\scripts\check_prereqs.ps1
Set-Location (Split-Path -Parent $PSScriptRoot)
$llm = if ($env:LLM_MODEL) { $env:LLM_MODEL } else { "qwen2.5:3b" }
$embed = if ($env:EMBED_MODEL) { $env:EMBED_MODEL } else { "nomic-embed-text" }
$script:fail = $false
function Ok($m) { Write-Host "  [OK]   $m" -ForegroundColor Green }
function Bad($m, $fix) { Write-Host "  [FAIL] $m`n         -> $fix" -ForegroundColor Red; $script:fail = $true }

Write-Host "Checking RAG demo prerequisites..."
if (Get-Command uv -ErrorAction SilentlyContinue) { Ok "uv $((uv --version).Split(' ')[1])" }
else { Bad "uv not found" 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"' }

$py = ".venv\Scripts\python.exe"
if (Test-Path $py) {
    Ok "virtual env .venv ($(& $py --version))"
    $v = & $py -c "import importlib.metadata as m; print(m.version('langflow'))" 2>$null
    if ($LASTEXITCODE -eq 0) { Ok "langflow $v" } else { Bad "langflow not installed in .venv" "uv pip install -r requirements.txt" }
} else { Bad ".venv missing" "uv venv --python 3.12; uv pip install -r requirements.txt" }

if (Get-Command ollama -ErrorAction SilentlyContinue) { Ok "ollama binary" }
else { Bad "ollama not found" "install OllamaSetup.exe (per-user, no admin) from https://ollama.com/download" }
try {
    $tags = Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 5
    Ok "ollama server on :11434"
    foreach ($m in @($llm, $embed)) {
        if ($tags.models.name -match [regex]::Escape($m.Split(':')[0])) { Ok "model $m" } else { Bad "model $m missing" "ollama pull $m" }
    }
} catch { Bad "ollama server not reachable on :11434" "start the Ollama app or run: ollama serve" }

try { Invoke-RestMethod http://127.0.0.1:7860/health -TimeoutSec 3 | Out-Null; Ok "Langflow already running on :7860" }
catch {
    if (Get-NetTCPConnection -LocalPort 7860 -State Listen -ErrorAction SilentlyContinue) {
        Bad "port 7860 is used by another app" "uv run langflow run --port 7861 --env-file .env"
    } else { Ok "port 7860 free" }
}
if (Test-Path .env) { Ok ".env present" } else { Bad ".env missing" "Copy-Item .env.example .env" }

if ($script:fail) { Write-Host "Fix the items above."; exit 1 }
Write-Host "All good - start with: uv run langflow run --env-file .env"

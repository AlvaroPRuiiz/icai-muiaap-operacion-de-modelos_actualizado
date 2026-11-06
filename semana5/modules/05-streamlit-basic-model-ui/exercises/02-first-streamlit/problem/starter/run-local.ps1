$ErrorActionPreference = "Stop"
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "../../../../../../..")).Path
$bundlePath = Join-Path $repositoryRoot "semana4/modules/04-model-packaging/exercises/01-model-packaging/01.02-serializable-inference-module/problem/starter/models/wine_quality_bundle"
if (-not (Test-Path -LiteralPath (Join-Path $bundlePath "manifest.json")) -or
    -not (Test-Path -LiteralPath (Join-Path $bundlePath "model.joblib"))) {
    throw "Falta el bundle real de S4 en $bundlePath"
}
$env:MODEL_UI_BUNDLE = $bundlePath
Push-Location $PSScriptRoot
try {
    uv run --with 'streamlit>=1.40,<2.0' streamlit run app.py
} finally {
    Pop-Location
}

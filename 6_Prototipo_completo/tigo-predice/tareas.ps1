<#
  Tareas de Tigo Predice (equivalente a un Makefile en Windows).

  Uso:  .\tareas.ps1 <tarea>

  preparar   Genera datos, entrena, registra la huella SHA-256 de los modelos y evalúa (todo el pipeline de IA)
  datos      Genera los datos sintéticos (móvil + hogar, semilla fija)
  entrenar   Entrena los modelos (móvil 72 h, hogar 7 días y Fase 2) y los firma (SHA-256)
  evaluar    Escribe reports/modelo.md
  front      Compila la interfaz (frontend/dist)
  test       Corre los tests de Python y del frontend
  lint       Revisa estilo y reglas de seguridad (ruff + eslint)
  seguridad  Análisis estático (reglas S), auditoría de dependencias y pruebas de ataque
  dev        Backend (puerto 8000) + interfaz con recarga en vivo (puerto 5173)
  demo       Inicia la demo (igual que iniciar_demo.bat)
#>
param([Parameter(Mandatory = $true)][string]$tarea)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
# Recarga el PATH por si Node o Python se instalaron después de abrir la terminal
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
$py = "$env:USERPROFILE\.venvs\tigo-predice\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "No existe el entorno $py. Ejecute iniciar_demo.bat una vez." }

switch ($tarea) {
    "datos"    { & $py -m ml.generar_datos; & $py -m ml.generar_hogar }
    "entrenar" { & $py -m ml.entrenar; & $py -m ml.entrenar_72h; & $py -m ml.entrenar_hogar }
    "evaluar"  { & $py -m ml.evaluar; & $py -m backend.app.services.roi | Out-Null; & $py -m backend.app.services.produccion | Out-Null }
    "preparar" {
        & $py -m ml.generar_datos; & $py -m ml.generar_hogar
        & $py -m ml.entrenar; & $py -m ml.entrenar_72h; & $py -m ml.entrenar_hogar
        & $py -m ml.evaluar; & $py -m backend.app.services.roi | Out-Null; & $py -m backend.app.services.produccion | Out-Null
    }
    "front"    { Push-Location frontend; npm run build; Pop-Location }
    "test"     { & $py -m pytest -q; Push-Location frontend; npx vitest run; Pop-Location }
    "lint"     { & $py -m ruff check .; Push-Location frontend; npx eslint .; Pop-Location }
    "seguridad" {
        & $py -m ruff check --select S .
        & $py -m pip_audit -r requirements.lock --progress-spinner off
        Push-Location frontend; npm audit --omit=dev; Pop-Location
        & $py -m pytest -q tests/test_seguridad.py tests/test_guardrails.py
    }
    "dev" {
        Start-Process -FilePath $py -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--port", "8000", "--reload"
        Push-Location frontend; npm run dev; Pop-Location
    }
    "demo"     { & "$PSScriptRoot\iniciar_demo.bat" }
    default    { Get-Help $PSCommandPath; exit 1 }
}

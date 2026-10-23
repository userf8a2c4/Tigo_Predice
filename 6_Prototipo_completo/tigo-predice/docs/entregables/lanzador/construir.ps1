# Compila Abrir_Demo.exe con el compilador de C# que trae Windows (.NET Framework 4).
# Uso: .\construir.ps1 -Salida <carpeta>\Abrir_Demo.exe   (Demo_Tigo_Predice.html va en la misma carpeta)
param(
    [Parameter(Mandatory = $true)][string]$Salida
)
$ErrorActionPreference = "Stop"
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$csc = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$tmp = Join-Path $env:TEMP "tigo-lanzador"
New-Item -ItemType Directory -Force $tmp | Out-Null

# Ícono: cuadrado azul Tigo con una onda celeste
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 64, 64
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = "AntiAlias"
$g.Clear([System.Drawing.Color]::Transparent)
$fondo = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(0, 55, 123))
$ruta = New-Object System.Drawing.Drawing2D.GraphicsPath
$ruta.AddArc(0, 0, 20, 20, 180, 90); $ruta.AddArc(44, 0, 20, 20, 270, 90)
$ruta.AddArc(44, 44, 20, 20, 0, 90); $ruta.AddArc(0, 44, 20, 20, 90, 90); $ruta.CloseFigure()
$g.FillPath($fondo, $ruta)
$lapiz = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(0, 200, 255)), 6
$lapiz.StartCap = "Round"; $lapiz.EndCap = "Round"
$g.DrawArc($lapiz, 14, 18, 36, 36, 200, 140)
$g.FillEllipse((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)), 27, 38, 10, 10)
$g.Dispose()
$ico = Join-Path $tmp "icono.ico"
$f = [System.IO.File]::Create($ico)
[System.Drawing.Icon]::FromHandle($bmp.GetHicon()).Save($f)
$f.Close()

& $csc /nologo /target:winexe /optimize+ "/out:$Salida" "/win32icon:$ico" `
    /reference:System.Windows.Forms.dll (Join-Path $aqui "Lanzador.cs")
if ($LASTEXITCODE -ne 0) { throw "csc falló" }
Write-Output "OK $Salida"

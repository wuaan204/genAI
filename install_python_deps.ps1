Param(
    [string]$PythonExe = "py"
)

$requirementsPath = "backend\requirements.txt"

if (-not (Test-Path $requirementsPath)) {
    Write-Error "Khong tim thay file $requirementsPath"
    exit 1
}

Write-Host "==> Cap nhat pip"
& $PythonExe -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "==> Cai dat thu vien tu $requirementsPath"
& $PythonExe -m pip install -r $requirementsPath

exit $LASTEXITCODE


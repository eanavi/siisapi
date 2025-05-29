# run_backend.ps1
# Ejecuta el backend FastAPI desde siisapi

# Ruta del backend
$backendPath = "G:\prg\python\siisapi"

# Activar entorno virtual
. "$backendPath\.entv\Scripts\Activate.ps1"

# Establecer PYTHONPATH
$env:PYTHONPATH = "$backendPath"

# Cambiar a la carpeta del backend
Set-Location $backendPath

# Ejecutar FastAPI con recarga
uvicorn app.principal:app --reload

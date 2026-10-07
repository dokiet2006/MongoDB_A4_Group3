$out = "evidence\env_check.txt"
function Log($t) { Add-Content -Path $out -Value $t -Encoding utf8 }
Set-Content -Path $out -Value ("Checked: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) -Encoding utf8
Log "=== Hardware ==="
Log ((Get-CimInstance Win32_ComputerSystem | ForEach-Object { "RAM_GB=" + [math]::Round($_.TotalPhysicalMemory/1GB,1) }))
Log ((Get-CimInstance Win32_Processor | ForEach-Object { $_.Name + " cores=" + $_.NumberOfCores + " threads=" + $_.NumberOfLogicalProcessors }))
Log ((Get-PhysicalDisk | ForEach-Object { $_.FriendlyName + " " + $_.MediaType }))
Log ("C_free_GB=" + [math]::Round((Get-PSDrive C).Free/1GB,1))
Log "=== Docker ==="
Log (docker --version)
Log (docker compose version)
Log (docker info --format "CPUs={{.NCPU}} MemTotal={{.MemTotal}}")
Log "=== MongoDB (image mongo:8.0) ==="
Log ((docker run --rm mongo:8.0 mongod --version | Select-Object -First 1))
Log ("mongosh " + (docker run --rm mongo:8.0 mongosh --version))
Log ((docker run --rm mongo:8.0 mongoimport --version | Select-Object -First 1))
Log (docker image inspect mongo:8.0 --format "{{.RepoDigests}}")
Log "=== Python ==="
Log (python --version)
Log (python -c "import pymongo, pandas; print('pymongo', pymongo.version, 'pandas', pandas.__version__)")
Get-Content $out

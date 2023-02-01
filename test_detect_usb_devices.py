

import subprocess


out = subprocess.run("PowerShell get-pnpdevice -instanceid 'USB*' -status OK")

# out = subprocess.getoutput("PowerShell -Command \"& {   Get-PnpDevice | Select-Object Status,Class,FriendlyName,InstanceId | ConvertTo-Json}\"")
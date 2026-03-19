# Windows Local Enumeration & Privilege Escalation (CRT-Focused)

Goal: Escalate from low-priv user to Administrator or access protected data.



# 1. Initial Context

```
whoami
whoami /priv
whoami /groups
hostname
systeminfo
```

Check:
- OS version
- Privileges
- Group membership



# 2. User Enumeration

```
net user
net localgroup administrators
```



# 3. Check Installed Patches

```
wmic qfe get Caption,Description,HotFixID,InstalledOn
```



# 4. Services (Very Important)

```
sc query
sc qc <service>
```

Check:
- Service running as SYSTEM
- Writable service binary path
- Unquoted service paths



# 5. Scheduled Tasks

```
schtasks /query /fo LIST /v
```

Check:
- Tasks running as SYSTEM
- Writable task binaries



# 6. AlwaysInstallElevated

Check:

```
reg query HKLM\Software\Policies\Microsoft\Windows\Installer
reg query HKCU\Software\Policies\Microsoft\Windows\Installer
```

If set to 1:
MSI execution as SYSTEM possible.



# 7. Writable Directories

```
icacls "C:\Program Files\SomeApp"
```

Look for:
- (F) or (M) permissions for Users



# 8. Stored Credentials

```
cmdkey /list
```

Check registry:

```
reg query HKLM /f password /t REG_SZ /s
```



# 9. Unquoted Service Path

If path:

```
C:\Program Files\Some Service\service.exe
```

Without quotes and writable directory in chain → drop malicious exe.



# 10. Token Privileges

If SeImpersonatePrivilege present:

JuicyPotato-type attacks (if allowed).

Check:

```
whoami /priv
```



# 11. UAC Bypass (If admin but limited)

Check if user in Administrators:

```
net localgroup administrators
```



# 12. File System Search

Search for creds:

```
dir /s *pass*
dir /s *.config
```



# 13. Quick Manual Workflow

1. whoami /priv
2. net user
3. net localgroup administrators
4. sc query
5. schtasks /query
6. check writable service paths
7. check AlwaysInstallElevated



# 14. Panic Mode Checklist

```
whoami /priv
net user
net localgroup administrators
sc query
schtasks /query /fo LIST /v
cmdkey /list
reg query HKLM\Software\Policies\Microsoft\Windows\Installer
```

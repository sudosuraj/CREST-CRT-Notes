
# Nessus Setup & Usage (CRT-Oriented)

Nessus is a vulnerability scanner used to identify:
- Missing patches
- Weak configurations
- Exposed services
- Known vulnerabilities
- SSL/TLS weaknesses
- Default credentials
- Anonymous access

# 1. Starting Nessus

## Check if Nessus is currently running

```
sudo systemctl status nessusd
netstat -tulnp | grep 8834
ss -tulnp | grep 8834
ps aux | grep nessus
```

## Start Service

```
sudo systemctl start nessusd
```

Access via browser:

```
https://127.0.0.1:8834
```

Login with configured credentials.

# 2. Create New Scan

Click:
```
New Scan → Basic Network Scan
```

Name:
```
CRT-Scan
```

Targets:
```
<IP>
```

Or multiple:
```
<IP1>, <IP2>, <Subnet>
```



# 3. Recommended Settings (Fast & Practical)

## Discovery

Enable:
- Ping
- TCP scan

## Port Scanning

Use:
- Default or All Ports (if time allows)

## Credentials (If You Have Them)

Add:
- SSH credentials (Linux)
- SMB credentials (Windows)

Credentialed scans reveal:
- Patch levels
- Missing updates
- Misconfigurations



# 4. Start Scan

Click:
```
Launch
```

Let it run in background.

Continue manual enumeration while scanning.


# Quick Checklist for Advanced Scan

1. Advanced Scan: host and name:
2. Port scanning: insert ports from nmap
3. Discovery: Change DTLS to known DTLS ports
4. Report: Enable Override Normal Verbosity Report as much info as possible:
5. Disbale Show missing patches have been superseded
6. Then run nessus
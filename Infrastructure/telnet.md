
# Telnet (TCP/23)

Telnet is an unencrypted remote terminal protocol.  
All credentials and data are transmitted in cleartext.

In CRT-style environments, Telnet commonly leads to:
- Weak credential compromise
- Credential reuse
- Lateral movement
- Cleartext password capture



# 1. Detection

## Nmap

```
nmap -p 23 -sV <IP>
nmap -p 23 --script telnet-encryption <IP>
```

Look for:
- Service banner
- Embedded device identifiers
- OS version leakage



# 2. Manual Connection

```
telnet <IP>
```

If prompted:

```
login:
password:
```

Try:
- Default credentials
- Credential reuse from other services
- Username enumeration via error messages



# 3. Default Credentials (Common Devices)

Test combinations such as:

```
admin:admin
admin:password
root:root
root:toor
cisco:cisco
```

If SNMP or web exposed earlier, reuse credentials.



# 4. Brute Force (If Allowed in Scope)

Using Hydra:

```
hydra -l admin -P wordlist.txt telnet://<IP>
hydra -L users.txt -P passwords.txt telnet://<IP>
```

Be mindful of:
- Lockout policies
- Rate limits



# 5. Cleartext Credential Capture

If you have network position (pivot or local capture):

## tcpdump

```
tcpdump -i eth0 port 23 -A
```

Look for:

```
login:
password:
```

Credentials appear in plaintext.

## Wireshark Filter

```
tcp.port == 23
```



# 6. Banner & OS Enumeration

After connecting:

```
?
help
uname -a
ver
```

Identify:
- Device type
- Underlying OS
- Limited shell vs full shell



# 7. Restricted Shell Escape

If limited environment:

Try:

```
sh
/bin/sh
bash
```

Or check for:

```
?
help
```

Sometimes embedded systems expose hidden commands.



# 8. Pivot Opportunity

If internal service reachable only via Telnet host:

Check:

```
netstat -an
ip a
route
```

Identify:
- Internal subnets
- Additional services



# 9. Telnet to Other Services

Some services expose Telnet internally on non-standard ports.

```
telnet <IP> <PORT>
```

Useful for:
- SMTP manual interaction
- HTTP manual requests
- Redis, etc.


# 10. Common Findings in CRT Context

- Telnet exposed externally
- Default credentials
- Shared credentials across services
- Cleartext password reuse
- Embedded device with outdated firmware
- Weak login banner information disclosure


# 11. Panic Mode Quick Checklist

```
nmap -p 23 -sV <IP>
telnet <IP>

admin:admin
root:root
cisco:cisco

hydra -l admin -P wordlist.txt telnet://<IP>

tcpdump -i eth0 port 23 -A
```

# 12. Impact Statement (Report Language)

"The Telnet service transmits authentication credentials in cleartext. An attacker with network access can intercept valid usernames and passwords, leading to full compromise of the affected system and potential lateral movement within the network."

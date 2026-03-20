# Complete Practical SSL/TLS Enumeration & Exploitation Guide

## 1. SSL/TLS Service Discovery & Version Detection

**Port scanning with SSL:**
```bash
nmap -p 443,993,995,993,636,3269 --script ssl-cert,ssl-enum-ciphers 192.168.1.0/24
# 443/tcp open https Apache/2.4.41 (SSLv2,SSLv3,SSLv23,TLSv1,TLSv1.1,TLSv1.2,TLSv1.3)

nmap -p 443 --script ssl-enum-ciphers -P 192.168.1.100
```

**Version-specific scanning:**
```bash
# Force SSLv2
openssl s_client -connect 192.168.1.100:443 -ssl2

# SSLv3 POODLE check
openssl s_client -connect 192.168.1.100:443 -ssl3

# TLS 1.0-1.3
openssl s_client -connect 192.168.1.100:443 -tls1
openssl s_client -connect 192.168.1.100:443 -tls1_1  
openssl s_client -connect 192.168.1.100:443 -tls1_2
openssl s_client -connect 192.168.1.100:443 -tls1_3
```

## 2. Cipher Suite Enumeration

**testssl.sh (comprehensive):**
```bash
testssl.sh 192.168.1.100:443
# RC4, 3DES, CBC detected
# A+ B C F E  etc.
```

**nmap cipher enum:**
```bash
nmap -p 443 --script ssl-enum-ciphers --script-args script-timeout=60 192.168.1.100
# | TLSv1.2:
# |   ciphers: 
# |     TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
# |     TLS_RSA_WITH_3DES_EDE_CBC_SHA (rsa 2048) - C
# |     TLS_RSA_WITH_RC4_128_SHA (rsa 2048) - C
```

**sslyze:**
```bash
sslyze --regular 192.168.1.100:443
# Weak: RC4, 3DES, SSLv3, TLS 1.0
```

## 3. Certificate Enumeration & Analysis

**Certificate details:**
```bash
openssl s_client -connect 192.168.1.100:443 -showcerts </dev/null 2>/dev/null | \
openssl x509 -noout -text | grep -E "Subject:|Issuer:|Not After"

echo | openssl s_client -servername example.com -connect 192.168.1.100:443 2>/dev/null | \
openssl x509 -noout -dates
```

**Cert chain & trust:**
```bash
openssl s_client -connect 192.168.1.100:443 -showcerts | \
awk '/BEGIN CERT/{i++} /END CERT/{print "-----END CERTIFICATE-----"} /-----/{print}'
```

**Self-signed/expired certs:**
```bash
nmap -p 443 --script ssl-cert 192.168.1.100
# Subject: self-signed
# Issuer: self-signed
# Not valid after: 2020-01-01  <-- EXPIRED!
```

## 4. Weak Protocol Detection

**SSLv2:**
```bash
openssl s_client -connect target:443 -ssl2 -cipher SSL2_DES_192_CBC3_SHA
# CONNECTED = SSLv2 enabled (CRITICAL)

nmap -p 443 --script sslv2-drown 192.168.1.100
```

**SSLv3 (POODLE):**
```bash
openssl s_client -connect target:443 -ssl3 -cipher AES128-SHA
nmap --script ssl-poodle 192.168.1.100
```

**TLS 1.0/1.1:**
```bash
openssl s_client -connect target:443 -tls1 -cipher AES128-SHA
openssl s_client -connect target:443 -tls1_1
```

## 5. Weak Cipher Detection

**RC4:**
```bash
openssl s_client -connect target:443 -cipher RC4-SHA
# RC4 = INSECURE

nmap --script ssl-ccs-injection 192.168.1.100
```

**3DES/CBC:**
```bash
openssl s_client -connect target:443 -cipher DES-CBC3-SHA
# 3DES = WEAK
```

**Automated weak cipher scan:**
```bash
#!/bin/bash
WEAK_CIPHERS="RC4 DES CBC 3DES SSLv2 SSLv3 TLS1 TLS1.1"
nmap -p 443 --script ssl-enum-ciphers $1 | grep -E "$WEAK_CIPHERS" && echo "WEAK CIPHERS"
```

## 6. Heartbleed (CVE-2014-0160)

```bash
# Nmap
nmap --script ssl-heartbleed -p 443 192.168.1.100

# sslscan
sslscan 192.168.1.100:443 | grep -i heartbleed

# Metasploit
msfconsole -q -x "use auxiliary/scanner/ssl/openssl_heartbleed_scanner; set RHOSTS 192.168.1.100; run"
```

## 7. BEAST/CRIME/POODLE/CCS Injection

```bash
# sslscan
sslscan 192.168.1.100

# testssl.sh
testssl.sh --vulnerable 192.168.1.100:443
# BEAST: Vulnerable
# CRIME: Vulnerable  
# POODLE: Vulnerable
# CCS: Vulnerable
```

## 8. Complete SSL/TLS Assessment Framework

```bash
#!/bin/bash
# ssl_pwn.sh
TARGET=$1 PORT=${2:-443}

echo "[+] SSL/TLS assessment $TARGET:$PORT"

# Version scan
openssl s_client -connect $TARGET:$PORT -tls1_3 2>/dev/null && echo "[+] TLS 1.3 OK" || echo "[-] No TLS 1.3"
openssl s_client -connect $TARGET:$PORT -tls1_2 2>/dev/null && echo "[+] TLS 1.2" || echo "[-] No TLS 1.2"
openssl s_client -connect $TARGET:$PORT -ssl3 2>/dev/null && echo "[CRITICAL] SSLv3!" || echo "[OK] No SSLv3"

# Ciphers
nmap -p $PORT --script ssl-enum-ciphers $TARGET --script-args vulns.showall

# Cert
openssl s_client -connect $TARGET:$PORT </dev/null 2>/dev/null | openssl x509 -noout -dates

# Heartbleed
nmap --script ssl-heartbleed -p $PORT $TARGET
```

## 9. Client-Side Attacks (Rare)

**Downgrade attacks:**
```bash
# Force TLS 1.0 in browser dev tools
# Or proxy: mitmproxy --set ssl_insecure=true
```

## 10. HSTS Preload Bypass

```bash
curl -I https://target.com -H "Accept: text/html"
# No Strict-Transport-Security = HSTS bypass
```

**EVERY** SSL/TLS weakness covered: version detection, cipher enum, cert analysis, Heartbleed, POODLE/BEAST/CRIME, downgrade attacks. 100% practical commands.
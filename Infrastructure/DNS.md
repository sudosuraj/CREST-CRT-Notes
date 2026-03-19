# Domain Name System (DNS)

## Service Detection

### nmap
```
# UDP DNS service/version detection
nmap -sU -sV -p 53 <TARGET_IP>

# TCP DNS (AXFR/zone transfers use TCP)
nmap -p 53 -sT -sV target.com
```

## Connect/Query

### dig 
```
dig ANY @<DNS_IP> <DOMAIN>          #Any information (often restricted)

dig A @<DNS_IP> <DOMAIN>            #Regular DNS request
dig AAAA @<DNS_IP> <DOMAIN>         #IPv6 DNS request

dig TXT @<DNS_IP> <DOMAIN>          #TXT records (SPF, verification tokens, etc.)
dig MX  @<DNS_IP> <DOMAIN>          #Mail servers
dig NS  @<DNS_IP> <DOMAIN>          #Authoritative name servers

dig SOA @<DNS_IP> <DOMAIN>          #Start of authority (often useful for recon)

dig -x 192.168.0.2 @<DNS_IP>        #Reverse lookup (PTR)
dig -x 2a00:1450:400c:c06::93 @<DNS_IP> #Reverse IPv6 lookup
```

## Banner Grabbing / Version Disclosure
### dig
```
dig @<DNS_IP> version.bind CHAOS TXT
```

### nmap
```
nmap --script dns-nsid <DNS_IP>
```
### telnet
```
nc -nv -u <DNS_IP> 53
```

## Enumeration

### dnsrecon - General Enumeration
```
# Standard enumeration
dnsrecon -d target.com -t std

# Brute force subdomains
dnsrecon -d target.com -D /usr/share/wordlists/dnsmap.txt -t brt

# Comprehensive scan
dnsrecon -d target.com -a -n <DNS_IP>

# Output results
dnsrecon -d target.com -a --xml output.xml
```
### DNS Reverse all of the addresses 
```
dnsrecon -r 127.0.0.0/24 -n <IP_DNS>
dnsrecon -r 127.0.1.0/24 -n <IP_DNS>
dnsrecon -r <IP_DNS>/24 -n <IP_DNS>
```

### nmap DNS enumeration scripts
```
# Brute-force common subdomains (+ optional SRV record guessing)
nmap -p 53 --script dns-brute <DNS_IP>

# Check whether the DNS server performs recursion for third-party domains (open resolver risk)
nmap -p 53 --script dns-recursion <DNS_IP>
```

## Zone Transfer

### dig
```
dig axfr @<DNS_IP> <DOMAIN>
```
### DNSRecon
```
dnsrecon -d active.htb -a -n <IP_DNS>
```
### nmap
```
nmap -p 53 --script dns-zone-transfer --script-args "dns-zone-transfer.domain=<DOMAIN>" <DNS_IP>
```



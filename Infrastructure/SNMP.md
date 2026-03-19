# Simple Network Management Protocol 


## Detection

### nmap
```
nmap -sU -p 161 target.com
nmap -sU -p 161 --script snmp-info target.com
```

### snmpget
```
snmpget -v1 -c public target.com .1.3.6.1.2.1.1.1.0
snmpget -v2c -c public target.com sysDescr.0
```

## Enumeration
### onesixtyone
```
onesixtyone -c /path/to/community_string_list.txt target.com
```

### nmap
```
nmap -sU -p 161 --script snmp-brute --script-args snmp-brute.communitiesdb=community_strings.txt target.com
```

### metasploit
```
msfconsole
msf > use auxiliary/scanner/snmp/snmp_login
msf auxiliary(scanner/snmp/snmp_login) > set RHOSTS target.com
msf auxiliary(scanner/snmp/snmp_login) > set PASS_FILE /path/to/community_wordlist.txt
msf auxiliary(scanner/snmp/snmp_login) > run
```


## Connect

## snmpwalk

### For SNMPv1/v2c (most common for pentesting due to weaker security)
```
snmpwalk -c <community_string> -v1 <target_ip>
snmpwalk -c <community_string> -v2c <target_ip>
```

### Walking the entire MIB tree
```
snmpwalk -c public -v2c 192.168.1.1
```

### Walking a specific OID
```
snmpwalk -c public -v2c 192.168.1.1 .1.3.6.1.2.1.1.1.0
```



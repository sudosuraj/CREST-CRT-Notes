# Network Time Protocol (UDP/123)

NTP (Network Time Protocol) synchronizes time across systems. From a pentest perspective, an exposed NTP server can leak **time**, **stratum/refid**, and sometimes **system/config variables** via control queries; misconfigurations may also expose **MRU/monitor data** (historically “monlist”) which reveals recent client IPs. Default: **UDP/123**. 

## Detecion

### nmap
```
nmap -sU -sV -p 123 <IP>
nmap -sU -p 123 --script ntp-info <IP>
nmap -sU -p 123 --script ntp-monlist <IP>
nmap -sU -p 123 --script "ntp* and (discovery or safe)" <IP>
```

## Enumeration

### nmap
```
nmap -sU -p 123 --script ntp-info <IP>
nmap -sU -p 123 --script ntp-info --script-args=ntp-info.timeout=5s <IP>
nmap -sU -p 123 --script ntp-monlist <IP>
```

### ntpq
```
ntpq -p pool.ntp.org      # query NTP server
ntpq -p <IP>              # peers / associations view (if allowed)
ntpq -c rv <IP>           # read variables (if allowed)
ntpq -c "rv 0" <IP>       # sometimes returns system vars
```

### ntpdate
```
ntpdate -q <IP>
```

### ntpdc (Mode 7 queries) - legacy
```
ntpdc -c sysinfo <IP>
ntpdc -c monlist <IP>     # if supported/exposed (legacy monitoring data)
```

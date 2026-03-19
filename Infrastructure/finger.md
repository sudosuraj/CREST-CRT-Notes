# Finger (TCP/79)

Finger is a legacy user-information service (`fingerd`) that can leak **usernames**, **full names (GECOS)**, **last login**, **idle time**, **home dirs**, **shells**, and sometimes **custom “plan/project”** files. It runs on **TCP/79**.

## Detection

### Nmap
```
nmap -p 79 -sV <IP>
nmap -p 79 --script finger <IP>
nmap -sV -sC -p 79 <IP>
```

## Banner Grabbing

#### netcat
```
nc -nv <IP> 79
```
#### telnet
```
telnet <IP> 79
```

## Manual Queries

### Querying a specific user
```
printf "root\r\n" | nc -nv <IP> 79
printf "admin\r\n" | nc -nv <IP> 79
printf "bob\r\n"   | nc -nv <IP> 79
```

### List Users 
```
printf "\r\n" | nc -nv <IP> 79
printf "\n"   | nc -nv <IP> 79
```

### Try common modifiers
```
printf "/W\r\n" | nc -nv <IP> 79      # “wide/verbose” on some servers
printf "root /W\r\n" | nc -nv <IP> 79
printf "root\r\n" | nc -nv <IP> 79 | sed -n '1,80p'
```

## Username Enumeration

### finger

#### Local
```
finger 
finger kwstas
```

#### Remote
```
finger @10.10.10.10
finger kwstas@10.0.57.12
```

### Nmap
```
nmap -p 79 --script finger <IP>
```

### Manual: check response differences
```
for u in root admin test user oracle; do
  echo "[*] $u"
  printf "$u\r\n" | nc -nv -w 3 <IP> 79
  echo
done

printf "thisuserdoesnotexist\r\n" | nc -nv -w 3 <IP> 79
```

**What you’re looking for**
- Different error text (e.g., “no such user” vs detailed fields)
- Different response length/timing
- Presence of GECOS fields, home dir, shell, last login, etc.
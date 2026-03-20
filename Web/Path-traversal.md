# Path Traversal

## Why It Matters

Path traversal lets an attacker escape the intended directory and access files elsewhere on the system. Depending on the application behavior, this can lead to:

- local file read
- source disclosure
- credential exposure
- inclusion-style escalation
- arbitrary file write in related contexts such as upload handling

## Recognition Cues

Look for parameters such as:

```text
page=
file=
path=
template=
download=
doc=
```

Strong hints:

- file download features
- image or document retrieval
- template selection
- errors leaking filesystem paths

## Workflow

1. identify a file-selection parameter
2. test straightforward traversal
3. try absolute paths and encoding bypasses
4. pull a safe proof file first
5. determine whether the issue stops at file read or can chain into inclusion or write abuse

## Step 1: Basic Traversal

Example:

```text
GET /download?file=report.pdf
GET /download?file=../../../../etc/passwd
```

Useful Linux targets:

- `/etc/passwd`
- `/etc/hosts`
- application source files
- `.env` and config files

Useful Windows targets:

- `C:\Windows\win.ini`
- `C:\Windows\System32\drivers\etc\hosts`
- `C:\inetpub\web.config`

## Step 2: Absolute Paths

If traversal sequences are blocked, try absolute paths:

```text
/etc/passwd
/var/www/html/index.php
C:\Windows\win.ini
C:\inetpub\web.config
```

## Step 3: Bypass Variants

If the app filters `../`, test:

```text
%2e%2e%2f
%252e%252e%252f
....//
..%2f
../../../../etc/passwd%00
../../../../etc/passwd/.
```

These are useful when:

- filtering is incomplete
- normalization happens in the wrong order
- extension appending is involved

## Extension And Suffix Tricks

If the app appends a suffix such as `.php`, try:

```text
../../../../etc/passwd%00
../../../../etc/passwd/.
```

This matters mostly in older or poorly implemented handling code.

## Burp And Manual Validation

When testing, compare:

- response size
- response structure
- clear file markers such as `root:x:0:0:`
- disclosed path fragments

Do not assume success from a status code alone.

## Where Traversal Leads Next

After confirming file read, prioritize:

- app source
- database configs
- `.env`
- credentials
- SSH keys
- logs

If the parameter truly includes rather than only reads files, this may overlap with LFI.

## Related Write Scenarios

Traversal also appears in:

- file upload destination handling
- archive extraction
- export or backup path selection

In those cases, the impact may become arbitrary file write rather than read.

## Pitfalls

- treating every filesystem error as confirmed traversal
- using only one traversal style
- pulling low-value files when config and source files would prove more
- missing Windows-style paths on Windows-backed apps

## Reporting Notes

Capture:

- the vulnerable parameter
- the successful traversal form
- the file(s) accessed
- whether source, config, or secrets were exposed
- any related escalation path such as inclusion or write impact

## Fast Checklist

```text
1. Find a file-selection parameter
2. Prove traversal with a safe target file
3. Try encoding and suffix bypasses
4. Pull source or config files next
5. Check whether the issue chains into LFI or file write
6. Save the request and file output
```

## ffuf

### Why It Matters

`ffuf` is not a finding by itself. It is a fast way to discover hidden content, virtual hosts, parameters, and value candidates that later lead to real findings.

Use it to answer:

- what content exists that the UI does not show?
- are there hidden routes or environments?
- are there undisclosed parameters?
- can I enumerate value space for an interesting parameter?

### Workflow

1. decide what you are fuzzing
2. choose the smallest useful wordlist
3. establish the baseline response to filter noise
4. fuzz one variable at a time
5. validate hits manually

### Common Modes

#### Directory Fuzzing

```bash
ffuf -u http://<ip>/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
ffuf -u http://<ip>/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -fs <size>
```

#### Extension Fuzzing

```bash
ffuf -w wordlist.txt:FUZZ -u http://<server>/indexFUZZ
```

#### Page Fuzzing

```bash
ffuf -u http://<server>/blog/FUZZ.php -w wordlist.txt
```

#### Recursive Fuzzing

```bash
ffuf -w wordlist.txt:FUZZ -u http://<server>/FUZZ -recursion -recursion-depth 1 -e .php -v
```

#### VHost Fuzzing

```bash
ffuf -w wordlist.txt:FUZZ -u http://target/ -H "Host: FUZZ.target" -fs <size>
```

#### Parameter Name Fuzzing

```bash
ffuf -w wordlist.txt:FUZZ -u http://target/admin.php?FUZZ=key -fs <size>
ffuf -w wordlist.txt:FUZZ -u http://target/admin.php -X POST -d "FUZZ=key" -H "Content-Type: application/x-www-form-urlencoded" -fs <size>
```

#### Parameter Value Fuzzing

```bash
ffuf -w ids.txt:FUZZ -u http://target/admin.php -X POST -d "id=FUZZ" -H "Content-Type: application/x-www-form-urlencoded" -fs <size>
```

### Filtering And Calibration

Always establish the baseline first:

- response size
- status code
- word count
- line count

Then filter:

- `-fs` for size
- `-fc` for status code
- `-fw` for word count

Without calibration, `ffuf` output is mostly noise.

### Wordlist Choices

Useful defaults:

```text
/usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt
/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

Use a focused list when you know the app context. Smaller, relevant lists usually outperform giant generic ones.

### Pitfalls

- fuzzing before you know the target behavior
- using huge wordlists without filtering
- trusting a hit without manual validation
- recursively fuzzing noisy routes

### Reporting Notes

`ffuf` itself is not normally the report item. Report the real thing it found:

- hidden admin route
- exposed backup
- vulnerable parameter
- alternate vhost

### Fast Checklist

```text
1. Choose the right fuzzing mode
2. Calibrate baseline response
3. Filter noise aggressively
4. Validate hits manually
5. Turn discoveries into real findings
```

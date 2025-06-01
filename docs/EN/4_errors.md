# Error Handling in the DAUPS Language

The DAUPS interpreter is designed to detect and report common runtime errors. Through static and dynamic analysis, it provides explicit messages that facilitate debugging and understanding of code behavior.

## Types of Detected Errors

| Error Type                    | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| Undeclared Variable           | Use of a variable not present in declarations                                |
| Uninitialized Variable        | Reading a variable before assignment                                         |
| Type Mismatch                 | Assignment or operation incompatible with the expected type                  |
| Unknown Function Call         | Invocation of a function that is undefined or misspelled                     |
| Incorrect Number of Arguments | Function call with too many or too few parameters                             |
| Out-of-Bounds Array Access    | Attempt to access an index that does not exist                                |
| Unsupported Type              | Use of a non-existent or malformed type                                       |
| Invalid Expression            | Incorrect syntax in an assignment or a conditional test                        |
| User Input Error              | Input of a value that does not conform to the variable's type                 |
| Invalid Instruction           | Unrecognized keyword or structure                                             |

## Examples of Errors and Corresponding Messages

### Undeclared Variable

~~~daups-docs
Algo
Begin
    x <-- 5  # x has not been declared
End
~~~

~~~text
RunTime error: Variable 'x' is not declared

    x <-- 5  # x has not been declared
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
~~~

### Type Mismatch

~~~daups-docs
Algo
    x : int
Begin
    x <-- "text"
End
~~~

~~~text
RunTime error: Variable 'x' is of type 'int', but got 'String'

    x <-- "text"
          ^^^^^^^
~~~

### Unknown Function Call

~~~daups-docs
Algo
    result : int
Begin
    result <-- unknown(3)
End
~~~

~~~text
RunTime error: 'unknown' is not defined

    result <-- unknown(3)
                 ^^^^^^^^^^
~~~

### Incorrect Number of Arguments

~~~daups-docs
function f(a : int, b : int) : int
    Begin
        return a + b
    End

Algo
Begin
    print f(3)  # one argument is missing
End
~~~

~~~text
RunTime error: 1 too few arguments passed into 'f'
Expected 2 arguments, got 1

    print f(3)  # one argument is missing
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
~~~

### Out-of-Bounds Array Access

~~~daups-docs
Algo
    tab : array of int
Begin
    tab <-- create_array(3)
    print tab[5]  # out of bounds
End
~~~

~~~text
RunTime error: Index access error (probably out of bounds)

    print tab[5]  # out of bounds
          ^^^^^^^^^^^^^^^^^^^^^
~~~

## Error Triggering

Errors are triggered either:

- **During static analysis** (declarations, types)
- **At runtime** (memory access, dynamic calls, user input)

The interpreter halts execution as soon as an error is detected, indicating precisely **the line concerned**, **the type of error**, and **the variable or function involved**.

## Best Practices to Avoid Errors

- Always declare variables with their type before ~Begin~.
- Respect types in assignments and function calls.
- Verify array dimensions before any index access.
- Read error messages carefully; they are designed to be explicit.
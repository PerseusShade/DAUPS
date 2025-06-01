# Execution Flow in the DAUPS Language

The DAUPS interpreter executes a program following a rigid, statically-typed structure in which blocks, variables, functions, and instructions are validated both statically and dynamically.

This chapter describes the complete execution pipeline, from loading a `.daups` file to producing the results.

## Main Execution Steps

1. Loading the source file
2. Lexical Analysis / Tokenization
3. Syntax Analysis
4. Semantic Analysis (types, functions, scopes…)
5. Symbol Table Construction
6. Line-by-Line Execution
7. Error Handling and Result Display

## 1. Loading the Source File

DAUPS source files are typically `.daups` or `.txt` files containing a structure such as:

```daups-docs
Algo
    a, b : int
Begin
    get a
    get b
    print a + b
End
```

The file is read in its entirety, and then each line is processed sequentially.

## 2. Syntax Analysis and Block Construction

The interpreter identifies the main blocks (`Algo`, `Begin`, `End`) and builds a logical representation of the program, including:

- Simple instructions (`get`, `print`, `x <-- 3`)
- Control blocks (`if`, `while`, `for`)
- Function definitions
- Variable declarations

## 3. Symbol Table

Declared variables and defined functions are recorded in a symbol table:

- Globally for the entire program
- Locally for each function's scope

Each symbol is associated with:

- a name
- a type (`int`, `float`, etc.)
- a value (initial or determined at runtime)
- a context (local or global)

## 4. Instruction Execution

The main block is executed in order of appearance. Each line may correspond to one of the following:

- an assignment
- a user input instruction
- a control structure
- a function call (built-in or user-defined)

Expressions are evaluated dynamically with type checking.

## 5. Function Calls

When a function is called:

- Arguments are evaluated
- A local context is created
- Local variables are isolated from the global environment
- A value is returned if the function specifies one

Example:

```daups-docs
function f(x : int) : int
    Begin
        return x * 2
    End

Algo
    y : int
Begin
    y <-- f(3)
    print y
End
```

## 6. Error Handling

Any error detected during execution (undeclared variable, type mismatch, index out of bounds, etc.) immediately halts the program with an explicit error message.

## 7. End of Execution

When all instructions in the main block have been executed:

- Results are displayed in the console (or captured if redirected)
- The program terminates normally if no error was raised

## Example of a Complete Executed Program

```daups-docs
Algo
    a, b : int
    result : int
Begin
    get a
    get b
    result <-- a + b
    print "Result :", result
End
```

## Summary

Execution in DAUPS follows a strict but predictable structure:

- No compilation: everything is interpreted dynamically
- Types and scopes are strictly enforced
- Error checking is systematic
- Functions and arrays are managed dynamically
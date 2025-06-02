# DAUPS Language Syntax

The DAUPS language is a pseudocode language with a rigid structure. It is designed to be easily readable and close to natural language, while enforcing a strict structure to guarantee correct execution.

## General Structure

A program begins with the keyword `Algo`, optionally followed by variable declarations. The main block is delimited by the keywords `Begin` and `End`.

```daups-docs
Algo
    Variable_declarations
Begin
    Instructions
End
```

## Comments

Comments start with `#` and extend to the end of the line.

```daups-docs
# This is a comment
get x  # This is also a comment
```

## Basic Types

The following data types are supported:

- `int`: integer
- `float`: real number
- `bool`: boolean
- `string`: string of characters
- `array of T`: array of type `T`, where `T` is one of the aforementioned types (including another array)

```daups-docs
x : int
text : string
list : array of int
matrix : array of array of float
```

## Variable Declaration

Variables must be declared **before the `Begin` block, within the `Algo` block**. Multiple variables of the same type can be declared together, separated by commas.

```daups-docs
Algo
    identifier_1 : type_1
    identifier_2_1, identifier_2_2 : type_2
Begin
    Instructions
End
```

## Assignment

The assignment operator is `<--`.

```daups-docs
Algo
    identifier_1 : type_1
    identifier_2_1, identifier_2_2 : type_2
Begin
    identifier_1 <-- value
    identifier_2_1 <-- expression
End
```

## Input / Output

### Reading (`get`)

```daups-docs
get identifier
get array[index]
```

### Printing (`print`)

```daups-docs
print "Identifier value:", identifier, "Saut-de-ligne"
```

> `"Saut-de-ligne"` is a special string representing a line break.

## Control Flow

### Conditional (`if`, `else if`, `else`)

```daups-docs
if Condition then
    Instructions
else if Condition then
    Instructions
else
    Instructions
```

Example:

```daups-docs
if x > 0 then
    print "Positive"
if x == 0 then
    print "Zero"
else
    print "Negative"
```

### Loops

#### While Loop (`while`)

```daups-docs
while (Condition)
    Instructions
```

#### For Loop (`for`)

```daups-docs
for i <-- 0 to 10
    print i
```

```daups-docs
for i <-- 10 downto 0
    print i
```

## Functions

A function is defined by the keyword `function`, followed by its name, typed parameters, return type (if any), and a `Begin`/`End` block.

```daups-docs
function name(param_1 : type_1, ...) : return_type
        var : type
    Begin
        Instructions
        return value
    End
```

Example:

```daups-docs
function maximum(a : int, b : int) : int
    Begin
        if a > b then
            return a
        else
            return b
    End
```

## Arrays

### Declaration

```daups-docs
t : array of int
mat : array of array of int
```

### Creation

```daups-docs
t <-- create_array(5)
mat <-- create_array(3, 4)
```

### Access

```daups-docs
t[0] <-- 42
get mat[i][j]
```

## Operations Permitted by Type

| Type     | Permitted Operations                                           |
|----------|----------------------------------------------------------------|
| `int`    | `+`, `-`, `*`, `/`, `div`, `mod`, `==`, `<`, `>`…              |
| `float`  | `+`, `-`, `*`, `/`, `==`, `<`, `>`…                            |
| `bool`   | `and`, `or`, `not`, comparisons                                |
| `string` | `+` (concatenation), comparisons (`==`, `!=`, etc.)            |
| `array`  | index access `t[i]`, size `size(t)`, creation                  |

## Important Notes

- Case is **sensitive** (`Variable`, `variable`, `VARIABLE` are distinct).
- Indentation is **mandatory**.
- The keyword `End` closes all blocks (main program and functions).
- Functions may call one another or be used within the main block.
- An error is raised if a variable is used without prior declaration.
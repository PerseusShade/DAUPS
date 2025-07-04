# Built-in Functions of the DAUPS Language

The **DAUPS** language provides several **built-in** functions, accessible directly without redefinition. They are automatically loaded into the global symbol table at each execution.

## List of Built-in Functions

| Name               | Description                                                   | Number of Arguments     | Example Call                              |
|--------------------|---------------------------------------------------------------|-------------------------|--------------------------------------------|
| `print`            | Displays one or more items without automatically adding a newline | 0 or more (unlimited)   | `print "Hello", x`                         |
| `get`              | Reads a user input and assigns it to a variable               | 1 (mandatory)           | `get x` or `get tab[i][j]`                 |
| `create_array`     | Creates an empty array of a given size                         | ≥1 (unlimited)          | `tab <-- create_array(3, 4)`              |
| `run`              | Executes another `.daups` (or `.txt`) file                       | 1 (string path)         | `run "example.daups"`                        |
| `SQRT`             | Computes the square root of a number                            | 1 (numeric)             | `print SQRT(25)`                           |
| `nombreAleatoire`  | Generates a random integer between two bounds                  | 2 (numeric)             | `nombreAleatoire(1, 100)`                 |
| `size`             | Returns the size of an array or a specific dimension           | 1 or 2 (array, [dim])   | `size(tab)` or `size(tab, 1)`             |
| `Pi`               | Mathematical constant (π)                                      | 0 (none)                | `print Pi`                                 |

## Details of Functions

### 🔹 `print ...`

Displays values without automatically appending a newline.

- **Arguments**: 0 or more (`string`, `int`, `float`, etc.)
  > `"Saut-de-ligne"` is a special string representing a newline.
- **Example**:
  ```daups-docs
  print "Bonjour", nom, 42
  ```

### 🔹 `get x`, `get tab[i]`

Prompts the user for input, dynamically typed according to the targeted variable.

- **Arguments**: 1 (target variable)
- **Example**:
  ```daups-docs
  get age
  get matrice[i][j]
  ```

### 🔹 `create_array(dim1, dim2, ...)`

Creates an empty array with one or more dimensions.

- **Arguments**: ≥1 (each argument represents a dimension, of type `int`)
- **Examples**:
  ```daups-docs
  tab <-- create_array(5)         # 1D array
  mat <-- create_array(4, 3)      # 2D array
  cube <-- create_array(2, 2, 2)   # 3D array
  ```

### 🔹 `run "path"`

Executes an external DAUPS file.

- **Arguments**: 1 (`string` – path to a `.daups` or `.txt` file)
- **Example**:
  ```daups-docs
  run "my_file.daups"
  ```

### 🔹 `SQRT(value)`

Returns the square root of a number.

- **Arguments**: 1 (`int` or `float`)
- **Example**:
  ```daups-docs
  r <-- SQRT(16)
  ```

### 🔹 `nombreAleatoire(min, max)`

Returns a random integer in the interval `[min, max]`.

- **Arguments**: 2 (`int` or `float`)
- **Example**:
  ```daups-docs
  n <-- nombreAleatoire(1, 10)
  ```

### 🔹 `size(array[, dimension])`

Returns the total size of an array or the size of a specific dimension.

- **Arguments**: 1 (array) or 2 (array, dimension)
- **Examples**:
  ```daups-docs
  print size(tab)         # total size
  print size(tab, 1)      # size of the 1st dimension
  ```

### 🔹 `Pi`

Floating-point constant equivalent to `π ≈ 3.141592653589793`.

- **Arguments**: 0
- **Example**:
  ```daups-docs
  print Pi
  ```
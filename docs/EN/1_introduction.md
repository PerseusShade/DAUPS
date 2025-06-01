# Introduction to the DAUPS Language

**DAUPS** is an educational programming language designed to promote structured learning of algorithmic thinking. It allows users to write, test, and execute algorithms using a strict, statically-typed syntax aligned with academic standards.

Developed in an academic context, DAUPS is primarily intended for beginner-level computer science students, providing a natural bridge between theoretical algorithms and practical programming.

## Language Objectives

DAUPS was designed to:

- Encourage rigorous writing of algorithms,
- Enforce explicit variable declarations with **static typing**,
- Improve error comprehension through clear runtime messages,
- Provide a complete development environment via a **dedicated Visual Studio Code extension**.

## Key Features

- **Explicit static typing**: each variable must be declared with a type (`int`, `float`, `string`, etc.) before use.
- **Mandatory declarations**: any undeclared or improperly used variable results in a runtime error.
- **Strict structure**: programs must start with `Algo`, contain a `Begin ... End` block, and may include typed functions.
- **Error detection**: the interpreter verifies type consistency, variable scope, and the validity of function calls.
- **Integrated ecosystem**: execution is handled by a Python-based interpreter, and the VS Code extension provides an interactive environment with syntax highlighting, autocompletion, tooltips, and direct execution.

## Running a DAUPS Program

To run DAUPS code:

1. Install the official extension from the Visual Studio Code marketplace: [https://vscode.com/extension](https://vscode.com/extension).
2. Create a new file with the `.daups` extension.
3. Write your algorithm following the language's syntax.
4. Click the **▷** button in the top bar to launch the interpreter.

The environment automatically reports syntax, type, or runtime errors and offers contextual suggestions through autocompletion and tooltips.

## Additional Resources

- **DAUPS Interpreter**: a Python-based execution engine.
- **VS Code Extension**: enhances code readability and interaction.
- **Online Documentation**: regularly updated and available in multiple languages.

If you have a question, suggestion, or notice an issue in this documentation, you may open an issue here:
[https://github.com/PerseusShade/DAUPS-docs/issues](https://github.com/PerseusShade/DAUPS-docs/issues)
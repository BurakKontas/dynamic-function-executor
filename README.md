# Dynamic Function Executor with PyQt6

This Python application allows you to dynamically execute functions with their parameters in a GUI interface created using PyQt6. It can read a list of functions, display their parameters as input fields, and execute the function with the provided values.

## Features

- Dynamically loads functions with their parameters.
- Automatically creates input fields for function parameters based on their types.
- Supports both primitive types (`int`, `str`, `float`, `bool`) and custom class types.
- Displays the function result in the GUI.
- Nested class handling: Class parameters are recursively handled to allow user input for nested classes.
- Handles primitive data types (like `int`, `str`, `float`, and `bool`) by displaying their names.
- Automatically displays tooltips with descriptions for non-primitive class instances.

## Installation

Make sure you have Python 3.x and `pip` installed. Then, install the required packages:

```bash
pip install PyQt6

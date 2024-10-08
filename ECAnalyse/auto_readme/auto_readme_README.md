This module is designed to automatically generate a README.md file for a given python module.

The README.md file is generated by extracting the relevant information from the functions and classes.

The README.md file is generated in the same directory as the python module.

The functions in this module are only used internally and it is not intended for the user to call them directly.


# Table of Contents

- [`auto_readme`](#`auto_readme`)
- [`new_section_begins`](#`new_section_begins`)
- [`section_title`](#`section_title`)
- [`doc_string`](#`doc_string`)
- [`add_bold_to_sections`](#`add_bold_to_sections`)

# `auto_readme`

**Arguments:**

- python_file_path: str

The path to the python file for which the README.md file is to be generated.



**Methodology:**

- Open the python file and read the contents.

- Extract the class and function names.

- For each class and function, extract the docstring.

- Write the extracted information to the README.md file.



**Examples:**

Before merging with main, the following should be ran to generate the README.md file:

```python

from ECAnalyse.auto_readme import auto_readme

auto_readme('/path/to/python/file.py')

```


# `new_section_begins`

**Arguments:**

- line: str

The line to be checked.



**Returns:**

- bool

True if line is start of new function or class, False otherwise.


# `section_title`

**Arguments:**

- line: str

Line which contains name of function or class



**Returns:**

- str

The title of the section formatted for the README.md file.


# `doc_string`

**Arguments:**

- python_file_contents: str

The contents of the python file.

- i: int

The index of the line where the class or function is defined.



**Returns:**

- str

The docstring of the function or class.


# `add_bold_to_sections`

**Arguments:**

- doc: str

The docstring of the class or function



**Returns:**

- str

The docstring with the sections bolded.



# Vernacular Programming Language - Complete Usage Guide

## Introduction
Vernacular 3.0 is an enterprise-ready natural language programming system that allows you to write programs using plain English commands. It supports both interactive REPL mode and script file execution with a professional command-line interface.

### 🆕 **New in Version 3.0: Python-Style Block Structure**
Vernacular now supports **Python-style indented blocks** alongside the original single-line syntax:

```vernacular
# Original single-line syntax (still supported)
if age is greater than 18 then print "Adult"
repeat 3 times: print "Hello"

# New Python-style block syntax
if age is greater than 18:
    print "You are an adult"
    print "You can vote"
    print "You have full rights"
```

## 🚀 **Getting Started**

### **Interactive REPL Mode**
```bash
python3 vernacular.py
```

You'll see:
```
=== Natural Language Programming REPL ===
Type commands in plain English. Type 'quit' to exit, 'help' for commands.

>>> 
```

### **Script Execution Mode**
```bash
python3 vernacular.py script.vern        # Execute a script file
python3 vernacular.py script.vern -v     # Execute with verbose output
python3 vernacular.py --help             # Show help and usage
python3 vernacular.py --version          # Show version information
```

### **Command Line Options**
- `--help` or `-h`: Show help message with examples
- `--version`: Display version information  
- `--verbose` or `-v`: Enable verbose execution output
- `script.vern`: Path to vernacular script file to execute

---

## 📜 **Script File Support**

### **Creating .vern Scripts**
Vernacular scripts use the `.vern` extension and support:
- **Comments**: Use `#` or `//` for line comments
- **All Commands**: Every command available in REPL works in scripts
- **Block Structure**: Python-style indented blocks with colons
- **Mixed Syntax**: Combine single-line and block structure in the same script
- **Error Reporting**: Line-by-line error reporting with statistics

### **Example Script Structure**
```vernacular
# My First Vernacular Script
# This demonstrates basic features

# Variables and output
set name to "Alice"
print "Hello"
print name

# Mathematics
add 10 and 5
calculate the square root of 144

# Lists and loops
create list numbers with 1, 2, 3, 4, 5
for each item in list numbers do print item

# Conditionals
if name equals "Alice" then print "Name matches!"
```

### **Example Scripts**
The `examples/` directory contains demonstration scripts:
- `examples/hello_world.vern` - Basic features showcase
- `examples/database_demo.vern` - Database operations demo  
- `examples/math_and_files.vern` - Mathematical computations and file I/O

### **Running Example Scripts**
```bash
python3 vernacular.py examples/hello_world.vern
python3 vernacular.py examples/database_demo.vern -v
python3 vernacular.py examples/math_and_files.vern
```

---

## 🐍 **Python-Style Block Structure**

### **Block Types Supported**
Vernacular 3.0 supports **7 different block types** with Python-style indentation:

#### **Conditional Blocks**
```vernacular
# Simple conditional block
if age is greater than 18:
    print "You are an adult"
    print "You can vote"
    print "You have full rights"

# Nested conditional blocks
if score is greater than 90:
    print "Excellent performance!"
    
    if score is greater than 95:
        print "Perfect score category"
        print "You deserve special recognition"
    
    print "You qualify for honors"
```

#### **Else Blocks**
```vernacular
if age is greater than 18:
    print "You are an adult"
else:
    print "You are a minor"
    print "You need parental consent"
```

#### **Loop Blocks**
```vernacular
# Repeat blocks
repeat 3 times:
    print "This is iteration number:"
    print "Loop body can contain multiple commands"
    print "Each command is properly indented"

# For each blocks
create list items with apple, banana, cherry
for each item in list items:
    print "Processing item:"
    print item
    print "Item processed successfully"

# While blocks
set counter to 0
while counter is less than 5:
    print "Counter value:"
    print counter
    increment counter
```

#### **Function Definition Blocks**
```vernacular
# Function without parameters
define function greet_user:
    print "Hello there!"
    print "Welcome to Vernacular 3.0"
    print "This is a block-structured function"

# Function with parameters
define function calculate_area with length, width:
    multiply length and width
    print "Area calculation complete"
    print result

# Call the functions
call function greet_user
call function calculate_area
```

### **Indentation Rules**
- **Spaces or Tabs**: Use spaces or tabs consistently (tabs = 4 spaces)
- **Consistent Indentation**: All commands in a block must have the same indentation level
- **Nested Blocks**: Deeper indentation creates nested blocks
- **Block Headers**: Lines ending with `:` start new blocks

### **Mixed Syntax Support**
You can combine both syntaxes in the same script:

```vernacular
# Single-line commands (original style)
set name to "Alice"
set age to 30
add 10 and 5

# Block structure (new style)
if age is greater than 25:
    print "You are in the adult category"
    print name
    print "is over 25 years old"

# Single-line conditional (original style)
if name equals "Alice" then print "Name matches Alice"

# Mixed function definitions
define function old_style as print "Single-line function"
define function new_style:
    print "Block-structured function"
    print "Can have multiple lines"
```

### **Supported Block Patterns**
- `if condition:` - Conditional blocks
- `else:` - Else blocks
- `for each item in list listname:` - For each loops
- `while condition:` - While loops
- `repeat N times:` - Repeat loops
- `define function name:` - Function definitions
- `define function name with params:` - Parameterized functions

---

## 📚 **Complete Feature Reference**

### 📝 **Basic Output**
Print text and variables to the console:
```vernacular
print "Hello, World!"
display "Welcome to vernacular"
show "This is output"
output "Testing"
print hello world
print variableName    # Prints the value of variable
```

### 🧮 **Mathematical Operations**

#### **Basic Arithmetic**
```vernacular
add 5 and 3
add -2.5 and 7.1          # Supports floats and negatives
calculate 10 + 7
subtract 2 from 10
multiply 4.5 by 6
divide 20 by 4
```

#### **Advanced Mathematics**
```vernacular
calculate the square root of 16
raise 2 to the power of 3
generate a random number between 1 and 100
round 3.14159 to 2 decimal places
calculate the sine of 45
calculate the cosine of 60
calculate the tangent of 30
calculate the natural log of 2.718
calculate the factorial of 5
calculate the absolute value of -42
```

#### **Statistics**
```vernacular
find the minimum of 5, 2, 8, 1, 9
find the maximum of 5, 2, 8, 1, 9
calculate the average of 5, 2, 8, 1, 9
```

### 📊 **Variables & Type System**

#### **Variable Creation**
```vernacular
set name to "John"
set age to 25
set price to 19.99
create variable city with value "New York"
create variable score = 95
```

#### **Type Checking & Conversion**
```vernacular
check type of name
is age a number
is name a string
convert age to string
convert name to number
convert value to boolean
```

#### **Variable Management**
```vernacular
list all variables
print name               # Print variable value
delete variable name
```

### 📋 **Lists**

#### **List Creation & Management**
```vernacular
create list fruits with apple, banana, cherry
create list numbers with 1, 2, 3, 4, 5
add orange to list fruits
show list fruits
list all lists
delete list fruits
```

#### **Anonymous Lists**
```vernacular
create a list with red, green, blue
add yellow to the list
show the list
```

### 🔤 **String Operations**
Manipulate text strings:
```vernacular
make "hello world" uppercase
make "HELLO WORLD" lowercase  
get the length of "programming"
reverse "hello"
replace "old" with "new" in "hello old world"
split "apple,banana,cherry" by ","
```

### ⚖️ **Conditional Statements**

#### **Single-Line Conditionals**
```vernacular
# Original single-line syntax
if name equals "John" then print "Name matches"
if age is greater than 18 then print "Adult"
if score is less than 90 then print "Below 90"

# Complex single-line conditionals
if age is greater than 18 and score is greater than 85 then print "Excellent"
if name equals "Alice" or name equals "Bob" then print "Match"
if not age equals 25 then print "Not 25 years old"
```

#### **Block-Structure Conditionals**
```vernacular
# Simple conditional blocks
if age is greater than 18:
    print "You are an adult"
    print "You can vote"
    print "You have full rights"

# Nested conditional blocks
if score is greater than 80:
    print "Good performance!"
    
    if score is greater than 95:
        print "Excellent work!"
        print "You deserve recognition"
    
    print "Keep up the good work"

# If-else blocks
if age is greater than 18:
    print "You are an adult"
    set status to "adult"
else:
    print "You are a minor"
    set status to "minor"
```

#### **Supported Conditional Operators**
- `equals` - Equality comparison
- `is greater than` - Greater than comparison
- `is less than` - Less than comparison
- `and` - Logical AND
- `or` - Logical OR
- `not` - Logical NOT

### 🔄 **Loops & Control Flow**

#### **Single-Line Loops**
```vernacular
# Original single-line syntax
repeat 5 times: print "Hello"
for each item in list numbers do print item
while counter is less than 10 do increment counter
count from 1 to 5 and print counter

# Advanced single-line loop controls
repeat 10 times: if counter equals 5 then break from loop
repeat 5 times: if counter equals 3 then continue with loop
for each item in list numbers do if item equals 3 then skip to next iteration
```

#### **Block-Structure Loops**
```vernacular
# Repeat blocks
repeat 3 times:
    print "This is iteration number:"
    print "Loop body can contain multiple commands"
    print "Each command is properly indented"

# For each blocks
create list items with apple, banana, cherry
for each item in list items:
    print "Processing item:"
    print item
    print "Item processed successfully"

# While blocks
set counter to 0
while counter is less than 5:
    print "Counter value:"
    print counter
    increment counter
```

#### **Nested Loops**
```vernacular
# Nested loop blocks
repeat 3 times:
    print "Outer loop iteration"
    
    repeat 2 times:
        print "Inner loop iteration"
        print "Nested processing"
    
    print "Outer loop continues"
```

#### **Loop Control Commands**
- `break from loop` - Exit the current loop
- `continue with loop` - Skip to next iteration
- `skip to next iteration` - Same as continue
- `exit the loop` - Same as break

### 🔧 **Functions**

#### **Single-Line Functions**
```vernacular
# Original single-line syntax
define function greet as print "Hello there"
define function add_numbers as add 10 and 5
call function greet
run greet                # Alternative syntax
```

#### **Block-Structure Functions**
```vernacular
# Function without parameters
define function greet_user:
    print "Hello there!"
    print "Welcome to Vernacular 3.0"
    print "This is a block-structured function"

# Function with parameters
define function calculate_area with length, width:
    multiply length and width
    print "Area calculation complete"
    print result

# Function with complex logic
define function process_data:
    print "Starting data processing"
    
    if data_exists then:
        print "Processing data"
        print "Data processing complete"
    else:
        print "No data to process"
    
    print "Function execution complete"

# Call the functions
call function greet_user
call function calculate_area
run process_data
```

#### **Function Features**
- **Parameters**: Functions can accept parameters
- **Multi-line**: Block functions can contain multiple commands
- **Nested Logic**: Functions can contain conditionals and loops
- **Local Scope**: Functions have their own variable scope
- **Both Syntaxes**: Single-line and block functions work together

### 📅 **Date and Time**
```vernacular
get the current time
get the current date
get the current datetime
add 7 days to today
subtract 3 days from today
```

---

## 🏢 **Enterprise Features**

### 📁 **File Operations**

#### **Text Files**
```vernacular
save "Hello, World!" to hello.txt
write "Some content" to data.txt
read hello.txt
load data.txt
check if file "test.txt" exists
```

#### **CSV Files**
```vernacular
create a CSV file data.csv with headers name, age, city
add row John, 25, NYC to CSV data.csv
add row Jane, 30, LA to CSV data.csv
read the CSV file data.csv
```

#### **JSON Files**
```vernacular
create list mydata with item1, item2, item3
save list mydata to output.json
load list from output.json
```

#### **XML Files**
```vernacular
save variables to data.xml
load variables from data.xml
```

#### **YAML Files**
```vernacular
save data to config.yaml
load data from config.yaml
```

### 🗄️ **Database Operations**

#### **Database Management**
```vernacular
create database "company_db"
connect to database "existing_db"
close database
```

#### **Table Operations**
```vernacular
create table employees with columns id integer, name text, age integer, salary real
list tables
describe table employees
drop table employees
```

#### **Data Operations**
```vernacular
insert into table employees values 1, "Alice Johnson", 28, 75000.50
select all from table employees
select name, salary from table employees
update table employees set salary = 80000 where name = "Alice Johnson"
delete from table employees where age < 25
```

### 🌐 **Web API Integration**

#### **HTTP Operations**
```vernacular
get data from "https://api.example.com/users"
post data to "https://api.example.com/users" with name=Alice, age=25
download file from "https://example.com/file.txt" to "local.txt"
check if "https://api.example.com" is accessible
get status of "https://api.example.com"
```

### 💾 **Session Management**
```vernacular
save session to "backup.json"
load session from "backup.json"
```

---

## 🔧 **System Commands**

### **Information & Management**
```vernacular
list all variables
list all lists
delete variable myvar
delete list mylist
reset everything
clear the screen
help
benchmark performance
```

### **Getting Help**
```vernacular
help                    # Show comprehensive help
what can you do         # Alternative help command
```

---

## 📊 **Performance & Debugging**

### **Performance Testing**
```vernacular
benchmark performance   # Run performance benchmark
```

### **Error Handling**
Vernacular provides intelligent error recovery:
- **Typo Correction**: `prin hello` → suggests `print "hello"`
- **Context Suggestions**: Shows available variables/lists/functions
- **Enhanced Messages**: Clear error descriptions with helpful tips

### **Generated Code**
The system shows generated Python code in brackets:
```
>>> add 5 and 3
5 + 3 = 8
[Generated: print(5.0 + 3.0)]
```

---

## 🎯 **Best Practices**

### **Script Development**
1. **Use Comments**: Document your scripts with `#` comments
2. **Organize Code**: Group related operations together
3. **Error Handling**: Check file existence before operations
4. **Test Incrementally**: Run scripts frequently during development

### **Syntax Guidelines**
1. **Quote Strings**: Use quotes for text: `"hello world"`
2. **Number Formats**: Supports integers, floats, and negatives
3. **File Extensions**: Include extensions: `.txt`, `.csv`, `.json`, `.xml`, `.yaml`
4. **Exact Syntax**: Follow examples precisely for best results

### **Common Patterns**
```vernacular
# Variables
set variableName to "value"
create variable variableName with value "value"

# Lists  
create list listName with item1, item2, item3
add newItem to list listName
show list listName

# Files
save "content" to filename.txt
read filename.txt

# Conditionals
if variable equals value then action
if variable is greater than number then action
```

---

## 📖 **Example Workflows**

### **Data Processing Workflow**
```vernacular
# Create and populate database
create database "sales_data"
create table sales with columns date text, amount real, region text

# Import data
insert into table sales values "2024-01-01", 1500.00, "North"
insert into table sales values "2024-01-02", 2300.50, "South"

# Analyze data
select all from table sales
calculate the average of 1500.00, 2300.50

# Export results
save variables to "analysis_results.xml"
close database
```

### **Mathematical Computing Workflow**
```vernacular
# Set up calculations
set radius to 5.5
set pi to 3.14159

# Calculate circle area
multiply radius and radius    # r²
multiply result and pi        # π × r²
print "Circle area:"
print result

# Statistical analysis
create list measurements with 12.5, 15.2, 18.7, 14.1, 16.9
calculate the average of measurements
find the maximum of measurements
find the minimum of measurements
```

### **Web Data Workflow**
```vernacular
# Fetch data from API
get data from "https://api.example.com/users"

# Process and store
create database "api_data"
create table users with columns id integer, name text, email text

# Save to multiple formats
save variables to "api_results.json"
save variables to "api_backup.xml"
```

---

## 🆘 **Troubleshooting**

### **Common Issues**
- **Command Not Recognized**: Check syntax against examples
- **File Not Found**: Verify file paths and existence
- **Database Errors**: Ensure database is created and connected
- **Network Errors**: Check URL accessibility and internet connection

### **Error Messages**
- `Sorry, I don't understand: 'command'` - Command syntax error
- `Error: Cannot divide by zero!` - Mathematical errors
- `Error: File 'filename' not found!` - File operation errors
- `Error: Variable 'name' doesn't exist!` - Variable access errors

### **Getting Support**
- Type `help` for command reference
- Check examples in `examples/` directory
- Review documentation in `context_data/` directory
- Use verbose mode (`-v`) for detailed execution information

---

## 📁 **Project Structure**

```
vernacular/
├── vernacular.py           # Main vernacular interpreter
├── examples/              # Example .vern scripts
│   ├── hello_world.vern   # Basic features demo
│   ├── database_demo.vern # Database operations demo
│   └── math_and_files.vern# Math and file operations demo
├── context_data/          # Documentation and reports
│   ├── USAGE_GUIDE.md     # This file
│   ├── TESTING_REPORT.md  # Comprehensive testing results
│   ├── MEMORY_NOTE.md     # Development context and history
│   ├── ENHANCEMENT_SUMMARY.md # Summary of improvements
│   └── EVALUATION_SUMMARY.md  # Original evaluation
└── tests/                 # Test files (for future test suite)
```

---

## 🎓 **Learning Path**

### **Beginner (Start Here)**
1. Run `python3 vernacular.py` to start REPL
2. Try basic commands: `print "hello"`, `add 5 and 3`
3. Create variables: `set name to "your name"`
4. Work with lists: `create list items with a, b, c`

### **Intermediate**
1. Learn conditionals: `if name equals "Alice" then print "match"`
2. Practice loops: `repeat 5 times: print "hello"`
3. Try file operations: `save "test" to "file.txt"`
4. Create simple scripts with `.vern` extension

### **Advanced**
1. Database operations: Create tables, insert data, query results
2. Web API integration: Fetch data from external sources
3. Complex scripts: Combine multiple features in `.vern` files
4. Performance optimization: Use benchmarking features

---

## 🏆 **Conclusion**

Vernacular 3.0 is a production-ready, enterprise-grade natural language programming system that makes programming accessible through intuitive English commands. Whether you're learning programming concepts, automating tasks, processing data, or building complex applications, vernacular provides a powerful yet approachable programming environment.

**Key Strengths:**
- **Intuitive**: Natural language syntax
- **Python-like**: Familiar block structure with indentation
- **Flexible**: Both single-line and block structure syntax
- **Powerful**: Enterprise features (database, web API, file I/O)
- **Backwards Compatible**: All existing scripts continue to work
- **Interactive**: Both REPL and script execution modes
- **Professional**: Command-line interface with proper error handling
- **Fast**: Optimized performance with 2.7x speedup

**New in Version 3.0:**
- **Python-Style Blocks**: Use indented blocks like Python
- **Enhanced Functions**: Multi-line functions with parameters
- **Nested Structures**: Complex nested logic with proper scoping
- **Mixed Syntax**: Combine single-line and block structure
- **Improved REPL**: Better piped input handling and error recovery

Start with simple commands in the REPL, progress to script files, and explore both single-line and block structure syntax. Vernacular bridges the gap between natural language and traditional programming, making it an ideal tool for education, prototyping, and specialized applications.
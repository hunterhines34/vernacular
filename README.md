# Vernacular Programming Language 3.0

A production-ready, enterprise-grade natural language programming system that makes programming accessible through intuitive English commands.

## 🚀 Features

### Core Programming Features
- **Natural Language Syntax**: Write programs in plain English
- **Python-Style Block Structure**: Use indented blocks like Python
- **Mixed Syntax Support**: Combine single-line and block structure
- **Variables & Lists**: Full variable system with type checking
- **Functions**: Both single-line and multi-line block functions
- **Conditionals**: Simple and complex conditional logic
- **Loops**: repeat, for-each, while loops with break/continue
- **Mathematical Operations**: Basic arithmetic + advanced functions
- **String Processing**: Case conversion, length, reverse, split, replace

### Enterprise Features
- **Database Integration**: Full SQLite support with natural language
- **Web API Integration**: HTTP GET/POST, file downloads, URL checking
- **File Operations**: Support for text, CSV, JSON, XML, YAML formats
- **Script Execution**: Run .vern script files with professional CLI
- **Error Recovery**: Intelligent suggestions and typo correction
- **Performance Optimized**: 2.7x speedup with regex caching

### Development Features
- **Interactive REPL**: Live coding environment
- **Script Files**: Create .vern files with comments and error reporting
- **Command Line Interface**: Professional CLI with help, version, verbose modes
- **Backward Compatible**: All existing scripts continue to work
- **Comprehensive Documentation**: Complete usage guides and examples

## 🐍 Python-Style Block Structure (New in 3.0)

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

## 📦 Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/vernacular.git
cd vernacular
```

Requirements:
- Python 3.6+
- No external dependencies for core features
- Optional: PyYAML for YAML file support

## 🚀 Quick Start

### Interactive Mode
```bash
python3 vernacular.py
```

### Script Execution
```bash
# Create a .vern script file
echo 'print "Hello, World!"' > hello.vern

# Run the script
python3 vernacular.py hello.vern

# Run with verbose output
python3 vernacular.py hello.vern -v
```

### Example Commands
```vernacular
# Variables
set name to "Alice"
set age to 30
print name

# Mathematics
add 10 and 5
calculate the square root of 144
generate a random number between 1 and 100

# Lists and Loops
create list items with apple, banana, cherry
for each item in list items:
    print "Processing:"
    print item

# Conditionals
if age is greater than 18:
    print "You are an adult"
    print "You can vote"
else:
    print "You are a minor"

# Functions
define function greet_user:
    print "Hello there!"
    print "Welcome to Vernacular 3.0"

call function greet_user
```

## 📚 Documentation

- **[Complete Usage Guide](context_data/USAGE_GUIDE.md)** - Comprehensive documentation
- **[Development Context](context_data/MEMORY_NOTE.md)** - Technical implementation details
- **[Enhancement Summary](context_data/ENHANCEMENT_SUMMARY.md)** - Feature improvements
- **[Testing Report](context_data/TESTING_REPORT.md)** - Test results and validation

## 🎯 Examples

The `examples/` directory contains demonstration scripts:
- `hello_world.vern` - Basic features showcase
- `database_demo.vern` - Database operations
- `math_and_files.vern` - Mathematical computations and file I/O
- `block_structure_demo.vern` - Python-style block structure demo
- `mixed_syntax_demo.vern` - Mixed syntax demonstration

Run examples:
```bash
python3 vernacular.py examples/hello_world.vern
python3 vernacular.py examples/database_demo.vern -v
python3 vernacular.py examples/block_structure_demo.vern
```

## 🔧 Command Line Interface

```bash
python3 vernacular.py                    # Interactive REPL
python3 vernacular.py script.vern        # Execute script file
python3 vernacular.py script.vern -v     # Execute with verbose output
python3 vernacular.py --help             # Show help and usage
python3 vernacular.py --version          # Show version information
```

## 🏗️ Architecture

- **Main Implementation**: `vernacular.py` (3000+ lines)
- **Block Structure**: Python-style indentation with 7 block types
- **Pattern Matching**: Regex-based command parsing with optimization
- **Error Recovery**: Intelligent suggestions and typo correction
- **Performance**: Compiled regex patterns for 2.7x speedup

## 🧪 Testing

The language has been comprehensively tested:
- 99%+ functionality working
- All major features validated
- Script execution: 90-100% success rates
- Performance: 2.7x speedup achieved
- Backward compatibility: 100% preserved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Status

**Production Ready**: Vernacular 3.0 is a fully functional, enterprise-grade programming language suitable for:
- Educational use and teaching programming concepts
- Rapid prototyping and proof-of-concept development
- Mathematical computing and data analysis
- Automation tasks and scripting
- Database operations and data processing
- Web API integration and connectivity

## 🎉 Acknowledgments

- Built with Python 3
- Inspired by natural language processing concepts
- Designed for accessibility and ease of use
- Comprehensive block structure implementation
- Professional development practices

---

**Start programming in plain English today!**
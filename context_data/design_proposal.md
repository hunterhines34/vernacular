# Vernacular 3.0: Python-Style Indentation Enhancement

## Overview
This proposal outlines the implementation of Python-style indentation and block structure for the vernacular programming language, creating a hybrid natural language/structured programming system.

## Design Goals

### 1. **Maintain Backward Compatibility**
- All existing .vern scripts continue to work unchanged
- Single-line commands remain fully supported
- REPL mode maintains current behavior

### 2. **Add Block Structure Support**
- Python-style indentation (4 spaces/tabs)
- Nested block support for complex logic
- Proper variable scoping within blocks
- Colon-terminated block headers

### 3. **Enhanced Language Features**
- Multi-line function definitions with parameters
- Complex conditional structures
- Nested loops and control flow
- Local variable scope management

## Syntax Examples

### Functions
```vernacular
# Current (single-line)
define function greet as print "Hello!"

# Enhanced (block structure)
define function greet:
    print "Hello!"
    print "Welcome to vernacular"

# With parameters
define function greet with name:
    print "Hello"
    print name
    print "Nice to meet you!"

# With multiple parameters
define function calculate_area with width, height:
    multiply width and height
    set result to calculation_result
    print "Area is:"
    print result
```

### Conditionals
```vernacular
# Current (single-line)
if age is greater than 18 then print "Adult"

# Enhanced (block structure)
if age is greater than 18:
    print "Adult"
    print "Can vote"
    if age is greater than 21:
        print "Can drink alcohol"
    else:
        print "Cannot drink yet"
else:
    print "Minor"
    print "Cannot vote"
```

### Loops
```vernacular
# Current (single-line)
repeat 3 times: print "Hello"

# Enhanced (block structure)
repeat 3 times:
    print "Hello"
    print "World"
    if counter equals 2:
        print "Middle iteration"

# For each with blocks
for each item in list numbers:
    print "Processing:"
    print item
    if item is greater than 5:
        print "Large number"
        add item to list large_numbers
    else:
        print "Small number"
```

### Complex Nested Structures
```vernacular
define function process_users with user_list:
    print "Processing users..."
    
    for each user in list user_list:
        print "Processing user:"
        print user
        
        if user contains "admin":
            print "Admin user detected"
            set admin_count to admin_count + 1
            
            if admin_count is greater than 5:
                print "Too many admins!"
                break from loop
        else:
            print "Regular user"
            add user to list regular_users
    
    print "Processing complete"
    print "Total admins:"
    print admin_count
```

## Implementation Architecture

### 1. **Block Parser System**
```python
class BlockParser:
    def __init__(self):
        self.indent_stack = []
        self.current_indent = 0
        self.block_queue = []
    
    def parse_script(self, lines):
        """Parse lines into hierarchical block structure"""
        blocks = []
        current_block = None
        
        for line_num, line in enumerate(lines, 1):
            indent_level = self.get_indent_level(line)
            content = line.strip()
            
            if self.is_block_start(content):
                # Start new block
                block = BlockContext(content, indent_level, line_num)
                if current_block and indent_level > current_block.indent:
                    current_block.add_child(block)
                else:
                    blocks.append(block)
                current_block = block
            else:
                # Add command to current block
                if current_block:
                    current_block.add_command(content, line_num)
                else:
                    # Top-level command
                    blocks.append(Command(content, line_num))
        
        return blocks
```

### 2. **Block Context Management**
```python
class BlockContext:
    def __init__(self, header, indent_level, line_number):
        self.header = header
        self.indent_level = indent_level
        self.line_number = line_number
        self.commands = []
        self.child_blocks = []
        self.parent = None
        self.variables = {}  # Local scope
    
    def add_command(self, command, line_num):
        self.commands.append(Command(command, line_num))
    
    def add_child(self, child_block):
        child_block.parent = self
        self.child_blocks.append(child_block)
    
    def execute(self, processor):
        """Execute this block with proper scope"""
        # Save current state
        old_vars = processor.variables.copy()
        
        # Execute header (if/while/function def)
        header_result = processor.process_block_header(self.header)
        
        if header_result.should_execute:
            # Execute commands in this block
            for command in self.commands:
                processor.process_command(command.content, context=self)
            
            # Execute child blocks
            for child in self.child_blocks:
                child.execute(processor)
        
        # Restore scope if needed
        if self.is_function_block():
            processor.variables = old_vars
```

### 3. **Enhanced Pattern System**
```python
# New block-starting patterns
BLOCK_PATTERNS = [
    (r"if (.+):$", self._if_block_start),
    (r"else:$", self._else_block_start),
    (r"for each (.+):$", self._foreach_block_start),
    (r"while (.+):$", self._while_block_start),
    (r"repeat (\d+) times?:$", self._repeat_block_start),
    (r"define function (\w+):$", self._function_block_start),
    (r"define function (\w+) with (.+):$", self._function_with_params_start),
]

# Keep existing single-line patterns for backward compatibility
SINGLE_LINE_PATTERNS = [
    (r"if (.+) then (.+)", self._if_single_line),
    (r"repeat (\d+) times?: (.+)", self._repeat_command),
    # ... existing patterns
]
```

### 4. **Scope Management**
```python
class ScopeManager:
    def __init__(self):
        self.scope_stack = []
        self.global_scope = {}
    
    def push_scope(self, block_context):
        """Enter new scope for block"""
        self.scope_stack.append(block_context.variables)
    
    def pop_scope(self):
        """Exit current scope"""
        return self.scope_stack.pop()
    
    def resolve_variable(self, name):
        """Resolve variable in current scope chain"""
        # Check local scopes first (innermost to outermost)
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        
        # Check global scope
        if name in self.global_scope:
            return self.global_scope[name]
        
        return None
```

## Migration Strategy

### 1. **Backward Compatibility**
- Existing .vern scripts work unchanged
- Single-line patterns have higher priority
- No breaking changes to current functionality

### 2. **Gradual Adoption**
- Users can mix single-line and block syntax
- Conversion tools for existing scripts
- Clear migration path and documentation

### 3. **Enhanced Features**
- Block syntax enables new capabilities
- Better code organization
- Improved maintainability

## Testing Strategy

### 1. **Backward Compatibility Tests**
- All existing example scripts must continue working
- REPL functionality unchanged
- Performance regression testing

### 2. **New Feature Tests**
- Block structure parsing
- Indentation validation
- Scope management
- Nested block execution

### 3. **Integration Tests**
- Mixed syntax scripts
- Complex nested structures
- Error handling and reporting

## Benefits

### 1. **For Beginners**
- Familiar block structure from other languages
- Better code organization
- Clearer program flow

### 2. **For Advanced Users**
- Complex logic structures
- Proper variable scoping
- Scalable application development

### 3. **For Education**
- Teaching programming concepts
- Structured thinking
- Bridge to traditional programming

## Implementation Timeline

### Phase 1: Block Parser (Week 1)
- BlockParser class implementation
- Basic indentation detection
- Simple block structure parsing

### Phase 2: Context Management (Week 2)
- BlockContext system
- Scope management
- Block execution engine

### Phase 3: Enhanced Patterns (Week 3)
- New block-starting patterns
- Backward compatibility layer
- Pattern priority system

### Phase 4: Advanced Features (Week 4)
- Function parameters
- Nested blocks
- Complex control flow

### Phase 5: Testing & Polish (Week 5)
- Comprehensive testing
- Documentation updates
- Performance optimization

## Conclusion

This enhancement will transform vernacular from a simple natural language interpreter into a powerful, structured programming language that maintains its accessibility while adding the organizational benefits of traditional programming languages. The implementation is feasible, valuable, and can be done while maintaining complete backward compatibility.
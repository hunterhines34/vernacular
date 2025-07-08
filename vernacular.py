#!/usr/bin/env python3
"""
Vernacular Programming Language 3.0
Supports both natural language commands and Python-style indentation
Full backward compatibility with single-line syntax
"""

import re
import sys
import math
import os
import random
import datetime
import csv
import json
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import argparse
from typing import List, Optional, Dict, Any

class BlockContext:
    """Represents a block of code with indentation"""
    def __init__(self, header: str, indent_level: int, line_number: int):
        self.header = header
        self.indent_level = indent_level
        self.line_number = line_number
        self.commands = []
        self.child_blocks = []
        self.parent = None
        self.block_type = self._determine_block_type(header)
        self.condition = None
        self.local_variables = {}  # For function scope
        
    def _determine_block_type(self, header: str) -> str:
        """Determine what type of block this is"""
        header = header.strip().lower()
        if header.startswith('if '):
            return 'conditional'
        elif header.startswith('else'):
            return 'else'
        elif header.startswith('for each'):
            return 'foreach'
        elif header.startswith('while '):
            return 'while'
        elif header.startswith('repeat '):
            return 'repeat'
        elif header.startswith('define function'):
            return 'function'
        return 'unknown'
    
    def add_command(self, command: str, line_num: int):
        """Add a command to this block"""
        self.commands.append({'command': command, 'line_number': line_num})
    
    def add_child_block(self, child_block):
        """Add a child block to this block"""
        child_block.parent = self
        self.child_blocks.append(child_block)
    
    def get_depth(self) -> int:
        """Get the depth of this block in the hierarchy"""
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

class BlockParser:
    """Parses script lines into block structure with Python-style indentation"""
    
    def __init__(self):
        self.blocks = []
        self.block_stack = []
        self.current_block = None
        
    def get_indent_level(self, line: str) -> int:
        """Calculate the indentation level of a line"""
        if not line:
            return 0
        
        # Count leading spaces and tabs (convert tabs to 4 spaces)
        indent = 0
        for char in line:
            if char == ' ':
                indent += 1
            elif char == '\t':
                indent += 4
            else:
                break
        return indent
    
    def is_block_start(self, content: str) -> bool:
        """Check if this line starts a block (ends with colon)"""
        if not content:
            return False
        
        content = content.strip()
        if not content.endswith(':'):
            return False
            
        # Check if it's a known block starter
        block_starters = [
            'if ', 'else:', 'for each ', 'while ', 'repeat ', 'define function'
        ]
        
        content_lower = content.lower()
        for starter in block_starters:
            if content_lower.startswith(starter):
                return True
        return False
    
    def parse_lines(self, lines: List[str]) -> List:
        """Parse lines into block structure"""
        self.blocks = []  # Reset blocks for each parse
        self.block_stack = []
        
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue
            
            indent_level = self.get_indent_level(line)
            content = stripped
            
            # Handle block structure
            if self.is_block_start(content):
                # This is a block header
                self._handle_block_start(content, indent_level, line_num)
            else:
                # This is a regular command
                self._handle_command(content, indent_level, line_num)
        
        # Close any remaining blocks
        self._close_all_blocks()
        
        return self.blocks
    
    def _handle_block_start(self, content: str, indent_level: int, line_num: int):
        """Handle the start of a new block"""
        # Close blocks that are at the same or higher indentation level
        while (self.block_stack and 
               self.block_stack[-1].indent_level >= indent_level):
            self.block_stack.pop()
        
        # Create new block
        block = BlockContext(content, indent_level, line_num)
        
        # Add to parent if we have one
        if self.block_stack:
            self.block_stack[-1].add_child_block(block)
        else:
            self.blocks.append(block)
        
        # Push to stack
        self.block_stack.append(block)
        self.current_block = block
    
    def _handle_command(self, content: str, indent_level: int, line_num: int):
        """Handle a regular command"""
        # Close blocks that are at higher indentation levels
        while (self.block_stack and 
               self.block_stack[-1].indent_level >= indent_level):
            closed_block = self.block_stack.pop()
            
        # Find the appropriate block for this command
        target_block = None
        for block in reversed(self.block_stack):
            if block.indent_level < indent_level:
                target_block = block
                break
        
        if target_block:
            target_block.add_command(content, line_num)
        else:
            # Top-level command - add to results directly
            self.blocks.append({'command': content, 'line_number': line_num})
    
    def _close_all_blocks(self):
        """Close all remaining blocks"""
        self.block_stack.clear()
        self.current_block = None

class NaturalLanguageProcessor:
    def __init__(self):
        # Block execution support
        self.block_parser = BlockParser()
        self.execution_context = []
        self.scope_stack = []
        
        # Define patterns: (regex_pattern, handler_function)
        # NOTE: Order matters! More specific patterns must come before general ones
        # New block-starting patterns (higher priority)
        self.block_patterns = [
            (r"if (.+):$", self._if_block_start),
            (r"else:$", self._else_block_start),
            (r"for each (.+):$", self._foreach_block_start),
            (r"while (.+):$", self._while_block_start),
            (r"repeat (\d+) times?:$", self._repeat_block_start),
            (r"define function (\w+):$", self._function_block_start),
            (r"define function (\w+) with (.+):$", self._function_with_params_start),
        ]
        
        # Original single-line patterns (for backward compatibility)
        self.patterns = [
            # Loop commands (must come before print commands)
            (r"repeat (\d+) times?: (.+)", self._repeat_command),
            (r"for each (?:item )?in list (\w+) do (.+)", self._foreach_list),
            (r"while (\w+) is less than (\d+) do (.+)", self._while_less_than),
            (r"count from (\d+) to (\d+) and (.+)", self._count_and_do),
            # Loop control commands
            (r"break (?:from )?(?:the )?loop", self._break_loop),
            (r"continue (?:with )?(?:the )?loop", self._continue_loop),
            (r"exit (?:the )?loop", self._break_loop),
            (r"skip (?:to )?(?:the )?next (?:iteration|item)", self._continue_loop),
            
            # Function-like operations (must come before print)
            (r"define function (\w+) as (.+)", self._define_function),
            (r"call function (\w+)", self._call_function),
            (r"run (\w+)", self._call_function),
            
            # Complex conditionals (must come before simple ones)
            (r"if (\w+) is greater than (\d+) and (\w+) is greater than (\d+) then (.+)", self._if_and_greater),
            (r"if (\w+) is less than (\d+) and (\w+) is less than (\d+) then (.+)", self._if_and_less),
            (r"if (\w+) equals? ['\"](.+?)['\"] and (\w+) equals? ['\"](.+?)['\"] then (.+)", self._if_and_equals),
            (r"if (\w+) is greater than (\d+) or (\w+) is greater than (\d+) then (.+)", self._if_or_greater),
            (r"if (\w+) is less than (\d+) or (\w+) is less than (\d+) then (.+)", self._if_or_less),
            (r"if (\w+) equals? ['\"](.+?)['\"] or (\w+) equals? ['\"](.+?)['\"] then (.+)", self._if_or_equals),
            (r"if not (\w+) equals? ['\"](.+?)['\"] then (.+)", self._if_not_equals),
            (r"if not (\w+) is greater than (\d+) then (.+)", self._if_not_greater),
            (r"if (\w+) is not equal to ['\"](.+?)['\"] then (.+)", self._if_not_equals),
            
            # Advanced conditionals (must come before print)
            (r"if (\w+) is greater than (\d+) then (.+)", self._if_greater_than),
            (r"if (\w+) is less than (\d+) then (.+)", self._if_less_than),
            (r"if (\w+) contains ['\"](.+?)['\"] then (.+)", self._if_contains),
            (r"if list (\w+) has (\d+) items? then (.+)", self._if_list_size),
            (r"if (\w+) equals? ['\"](.+?)['\"] then (.+)", self._if_equals),
            (r"if (\w+) equals? (\d+) then (.+)", self._if_equals),
            
            # Simple conditionals (legacy pattern)
            (r"if (\w+) equals? (\w+) then print ['\"](.+?)['\"]", self._simple_if),
            
            # Print commands (must come after loops, functions, conditionals)
            (r"print (?:the words? )?['\"](.+?)['\"]", self._print_quoted),
            (r"print (?:the )?(?:value of )?(\w+)", self._print_variable),
            (r"print (?:the words? )?(.+)", self._print_words),
            (r"display (?:the words? )?['\"](.+?)['\"]", self._print_quoted),
            (r"display (?:the )?(?:value of )?(\w+)", self._print_variable),
            (r"show (?:me )?(?:the words? )?['\"](.+?)['\"]", self._print_quoted),
            (r"show (?:me )?(?:the )?(?:value of )?(\w+)", self._print_variable),
            (r"output ['\"](.+?)['\"]", self._print_quoted),
            
            # Math commands (support integers, decimals, and negative numbers)
            (r"add (-?\d+(?:\.\d+)?) and (-?\d+(?:\.\d+)?)", self._add_numbers),
            (r"calculate (-?\d+(?:\.\d+)?) \+ (-?\d+(?:\.\d+)?)", self._add_numbers),
            (r"subtract (-?\d+(?:\.\d+)?) from (-?\d+(?:\.\d+)?)", self._subtract_numbers),
            (r"multiply (-?\d+(?:\.\d+)?) (?:by|and) (-?\d+(?:\.\d+)?)", self._multiply_numbers),
            (r"divide (-?\d+(?:\.\d+)?) by (-?\d+(?:\.\d+)?)", self._divide_numbers),
            (r"calculate the square root of (\d+(?:\.\d+)?)", self._square_root),
            (r"raise (-?\d+(?:\.\d+)?) to the power of (-?\d+(?:\.\d+)?)", self._power),
            (r"generate (?:a )?random number between (-?\d+) and (-?\d+)", self._random_number),
            (r"find the minimum of (.+)", self._find_minimum),
            (r"find the maximum of (.+)", self._find_maximum),
            (r"calculate the average of (.+)", self._calculate_average),
            (r"round (-?\d+\.?\d*) to (\d+) decimal places?", self._round_number),
            # Advanced math functions
            (r"calculate (?:the )?sine of (-?\d+(?:\.\d+)?)", self._sine),
            (r"calculate (?:the )?cosine of (-?\d+(?:\.\d+)?)", self._cosine),
            (r"calculate (?:the )?tangent of (-?\d+(?:\.\d+)?)", self._tangent),
            (r"calculate (?:the )?natural log(?:arithm)? of (\d+(?:\.\d+)?)", self._natural_log),
            (r"calculate (?:the )?log(?:arithm)? base (\d+) of (\d+(?:\.\d+)?)", self._log_base),
            (r"calculate (?:the )?absolute value of (-?\d+(?:\.\d+)?)", self._absolute_value),
            (r"calculate (?:the )?factorial of (\d+)", self._factorial),
            
            # String operations
            (r"make ['\"](.+?)['\"] uppercase", self._make_uppercase),
            (r"make ['\"](.+?)['\"] lowercase", self._make_lowercase),
            (r"get the length of ['\"](.+?)['\"]", self._string_length),
            (r"reverse ['\"](.+?)['\"]", self._reverse_string),
            (r"replace ['\"](.+?)['\"] with ['\"](.+?)['\"] in ['\"](.+?)['\"]", self._replace_string),
            (r"split ['\"](.+?)['\"] by ['\"](.+?)['\"]", self._split_string),
            
            # Date and time (datetime must come before date)
            (r"get (?:the )?current datetime", self._get_current_datetime),
            (r"get (?:the )?current time", self._get_current_time),
            (r"get (?:the )?current date", self._get_current_date),
            (r"add (\d+) days? to today", self._add_days_to_today),
            (r"subtract (\d+) days? from today", self._subtract_days_from_today),
            
            # Variable commands
            (r"set (\w+) to ['\"](.+?)['\"]", self._set_string_variable),
            (r"set (\w+) to (-?\d+(?:\.\d+)?)", self._set_number_variable),
            (r"create (?:a )?variable (?:called )?(\w+) (?:with value |= )(.+)", self._create_variable),
            # Type checking commands
            (r"check (?:the )?type of (\w+)", self._check_variable_type),
            (r"what (?:is the )?type of (\w+)", self._check_variable_type),
            (r"is (\w+) (?:a )?string", self._is_string_type),
            (r"is (\w+) (?:a )?number", self._is_number_type),
            (r"is (\w+) (?:a )?boolean", self._is_boolean_type),
            (r"convert (\w+) to string", self._convert_to_string),
            (r"convert (\w+) to number", self._convert_to_number),
            (r"convert (\w+) to boolean", self._convert_to_boolean),
            
            # List commands
            (r"create (?:a )?list (?:called )?(\w+) with (.+)", self._create_list),
            (r"create (?:a )?list with (.+)", self._create_anonymous_list),
            (r"add (.+) to (?:the )?list (\w+)", self._add_to_list),
            (r"add (.+) to (?:the )?list", self._add_to_anonymous_list),
            (r"show (?:the )?list (\w+)", self._show_list),
            (r"show (?:the )?list", self._show_anonymous_list),
            
            # File operations
            (r"check if file (\S+) exists", self._check_file_exists),
            (r"does file (\S+) exist", self._check_file_exists),
            (r"save ['\"](.+?)['\"] to (\S+\.txt)", self._save_to_file),
            (r"write ['\"](.+?)['\"] to (\S+\.txt)", self._save_to_file),
            (r"read (?:the contents of )?(\S+\.txt)", self._read_file),
            (r"load (\S+\.txt)", self._read_file),
            (r"create (?:a )?CSV file (\S+\.csv) with headers (.+)", self._create_csv),
            (r"add row (.+) to CSV (\S+\.csv)", self._add_csv_row),
            (r"read (?:the )?CSV file (\S+\.csv)", self._read_csv),
            (r"save list (\w+) to (\S+\.json)", self._save_list_to_json),
            (r"load list from (\S+\.json)", self._load_list_from_json),
            (r"save (?:data|variables) to (\S+\.xml)", self._save_to_xml),
            (r"load (?:data|variables) from (\S+\.xml)", self._load_from_xml),
            (r"save (?:data|variables) to (\S+\.ya?ml)", self._save_to_yaml),
            (r"load (?:data|variables) from (\S+\.ya?ml)", self._load_from_yaml),
            (r"delete file (\S+)", self._delete_file),
            (r"copy file (\S+) to (\S+)", self._copy_file),
            
            # Input/Output
            (r"ask (?:the user )?for (?:their )?(.+)", self._get_user_input),
            (r"get input for (.+)", self._get_user_input),
            (r"prompt (?:for )?(.+)", self._get_user_input),
            
            # System operations
            (r"save session to (\S+)", self._save_session),
            (r"load session from (\S+)", self._load_session),
            (r"save state to (\S+)", self._save_session),
            (r"load state from (\S+)", self._load_session),
            (r"clear (?:the )?screen", self._clear_screen),
            (r"list (?:all )?variables", self._list_variables),
            (r"list (?:all )?lists", self._list_lists),
            (r"delete variable (\w+)", self._delete_variable),
            (r"delete list (\w+)", self._delete_list),
            (r"reset everything", self._reset_all),
            
            # Help
            (r"help|what can you do", self._show_help),
            
            # Performance benchmarking
            (r"benchmark (?:performance|speed)", self._benchmark_command),
            
            # Database operations
            (r"create database ['\"](.+?)['\"]", self._create_database),
            (r"connect to database ['\"](.+?)['\"]", self._connect_database),
            (r"create table (\w+) with columns (.+)", self._create_table),
            (r"insert into table (\w+) values (.+)", self._insert_into_table),
            (r"select all from table (\w+)", self._select_all_from_table),
            (r"select (.+) from table (\w+)", self._select_from_table),
            (r"update table (\w+) set (.+) where (.+)", self._update_table),
            (r"delete from table (\w+) where (.+)", self._delete_from_table),
            (r"drop table (\w+)", self._drop_table),
            (r"list (?:all )?tables", self._list_tables),
            (r"describe table (\w+)", self._describe_table),
            (r"close database", self._close_database),
            
            # Web API integration
            (r"get (?:data )?from (?:url )?['\"](.+?)['\"]", self._http_get),
            (r"post (?:data )?to (?:url )?['\"](.+?)['\"] with data (.+)", self._http_post),
            (r"download (?:file )?from ['\"](.+?)['\"] (?:to|as) ['\"](.+?)['\"]", self._download_file),
            (r"check if (?:url )?['\"](.+?)['\"] is (?:accessible|available)", self._check_url),
            (r"get (?:the )?status of (?:url )?['\"](.+?)['\"]", self._get_url_status),
        ]
        
        # Store variables, lists, and functions
        self.variables = {}
        self.lists = {}
        self.functions = {}
        
        # Enhanced function storage for block-style functions
        self.block_functions = {}  # Functions defined with blocks
        self.current_list = []  # For anonymous list operations
        
        # Loop control flags
        self.break_loop = False
        self.continue_loop = False
        
        # Database connection
        self.db_connection = None
        self.db_cursor = None
        
        # Compile regex patterns for better performance
        self.compiled_patterns = []
        
        # Compile block patterns first (higher priority)
        self.compiled_block_patterns = []
        for pattern, handler in self.block_patterns:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.compiled_block_patterns.append((compiled_pattern, handler))
        
        # Compile single-line patterns (for backward compatibility)
        for pattern, handler in self.patterns:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.compiled_patterns.append((compiled_pattern, handler))
    
    def _print_quoted(self, match):
        """Handle quoted print statements"""
        text = match.group(1)
        print(text)
        return f'print("{text}")'
    
    def _print_variable(self, match):
        """Print the value of a variable"""
        var_name = match.group(1)
        if var_name in self.variables:
            value = self.variables[var_name]
            print(value)
            return f'print({var_name})'
        else:
            print(f"Error: Variable '{var_name}' is not defined!")
            if self.variables:
                available = ', '.join(list(self.variables.keys())[:5])
                print(f"Available variables: {available}")
                print(f"Tip: Create it first with 'set {var_name} to value'")
            else:
                print("No variables exist yet. Create one with 'set name to value'")
            return None
    
    def _print_words(self, match):
        """Handle unquoted print statements"""
        text = match.group(1).strip()
        print(text)
        return f'print("{text}")'
    
    def _add_numbers(self, match):
        """Handle addition"""
        a, b = float(match.group(1)), float(match.group(2))
        result = a + b
        # Display as int if result is whole number
        if result.is_integer():
            result = int(result)
            a_display = int(a) if a.is_integer() else a
            b_display = int(b) if b.is_integer() else b
        else:
            a_display, b_display = a, b
        print(f"{a_display} + {b_display} = {result}")
        return f"print({a} + {b})"
    
    def _subtract_numbers(self, match):
        """Handle subtraction"""
        a, b = float(match.group(2)), float(match.group(1))  # Note: "subtract X from Y" means Y - X
        result = a - b
        # Display as int if numbers are whole
        a_display = int(a) if a.is_integer() else a
        b_display = int(b) if b.is_integer() else b
        result_display = int(result) if result.is_integer() else result
        print(f"{a_display} - {b_display} = {result_display}")
        return f"print({a} - {b})"
    
    def _multiply_numbers(self, match):
        """Handle multiplication"""
        a, b = float(match.group(1)), float(match.group(2))
        result = a * b
        # Display as int if numbers are whole
        a_display = int(a) if a.is_integer() else a
        b_display = int(b) if b.is_integer() else b
        result_display = int(result) if result.is_integer() else result
        print(f"{a_display} * {b_display} = {result_display}")
        return f"print({a} * {b})"
    
    def _divide_numbers(self, match):
        """Handle division"""
        a, b = float(match.group(1)), float(match.group(2))
        if b == 0:
            print("Error: Cannot divide by zero!")
            return None
        result = a / b
        # Display as int if numbers are whole
        a_display = int(a) if a.is_integer() else a
        b_display = int(b) if b.is_integer() else b
        result_display = int(result) if result.is_integer() else result
        print(f"{a_display} / {b_display} = {result_display}")
        return f"print({a} / {b})"
    
    def _square_root(self, match):
        """Handle square root"""
        number = float(match.group(1))
        if number < 0:
            print("Error: Cannot calculate square root of negative number!")
            return None
        result = math.sqrt(number)
        number_display = int(number) if number.is_integer() else number
        result_display = int(result) if result.is_integer() else result
        print(f"√{number_display} = {result_display}")
        return f"print(math.sqrt({number}))"
    
    def _power(self, match):
        """Handle exponentiation"""
        base, exponent = float(match.group(1)), float(match.group(2))
        result = base ** exponent
        base_display = int(base) if base.is_integer() else base
        exp_display = int(exponent) if exponent.is_integer() else exponent
        result_display = int(result) if result.is_integer() else result
        print(f"{base_display}^{exp_display} = {result_display}")
        return f"print({base} ** {exponent})"
    
    def _random_number(self, match):
        """Generate random number in range"""
        min_val, max_val = int(match.group(1)), int(match.group(2))
        result = random.randint(min_val, max_val)
        print(f"Random number between {min_val} and {max_val}: {result}")
        return f"print(random.randint({min_val}, {max_val}))"
    
    def _find_minimum(self, match):
        """Find minimum value in a list of numbers"""
        values_str = match.group(1)
        try:
            values = [int(v.strip()) for v in values_str.split(',')]
            result = min(values)
            print(f"Minimum of {values}: {result}")
            return f"print(min({values}))"
        except ValueError:
            print("Error: Please provide comma-separated numbers")
            return None
    
    def _find_maximum(self, match):
        """Find maximum value in a list of numbers"""
        values_str = match.group(1)
        try:
            values = [int(v.strip()) for v in values_str.split(',')]
            result = max(values)
            print(f"Maximum of {values}: {result}")
            return f"print(max({values}))"
        except ValueError:
            print("Error: Please provide comma-separated numbers")
            return None
    
    def _calculate_average(self, match):
        """Calculate average of numbers"""
        values_str = match.group(1)
        try:
            values = [int(v.strip()) for v in values_str.split(',')]
            result = sum(values) / len(values)
            print(f"Average of {values}: {result:.2f}")
            return f"print(sum({values}) / len({values}))"
        except ValueError:
            print("Error: Please provide comma-separated numbers")
            return None
    
    def _round_number(self, match):
        """Round number to specified decimal places"""
        number, places = float(match.group(1)), int(match.group(2))
        result = round(number, places)
        print(f"{number} rounded to {places} decimal places: {result}")
        return f"print(round({number}, {places}))"
    
    def _sine(self, match):
        """Calculate sine of angle in degrees"""
        angle = float(match.group(1))
        # Convert degrees to radians
        radians = math.radians(angle)
        result = math.sin(radians)
        angle_display = int(angle) if angle.is_integer() else angle
        print(f"sin({angle_display}°) = {result:.6f}")
        return f"print(math.sin(math.radians({angle})))"
    
    def _cosine(self, match):
        """Calculate cosine of angle in degrees"""
        angle = float(match.group(1))
        radians = math.radians(angle)
        result = math.cos(radians)
        angle_display = int(angle) if angle.is_integer() else angle
        print(f"cos({angle_display}°) = {result:.6f}")
        return f"print(math.cos(math.radians({angle})))"
    
    def _tangent(self, match):
        """Calculate tangent of angle in degrees"""
        angle = float(match.group(1))
        radians = math.radians(angle)
        result = math.tan(radians)
        angle_display = int(angle) if angle.is_integer() else angle
        print(f"tan({angle_display}°) = {result:.6f}")
        return f"print(math.tan(math.radians({angle})))"
    
    def _natural_log(self, match):
        """Calculate natural logarithm"""
        number = float(match.group(1))
        if number <= 0:
            print("Error: Cannot calculate logarithm of zero or negative number!")
            return None
        result = math.log(number)
        number_display = int(number) if number.is_integer() else number
        print(f"ln({number_display}) = {result:.6f}")
        return f"print(math.log({number}))"
    
    def _log_base(self, match):
        """Calculate logarithm with specified base"""
        base, number = float(match.group(1)), float(match.group(2))
        if number <= 0 or base <= 0 or base == 1:
            print("Error: Invalid values for logarithm!")
            return None
        result = math.log(number) / math.log(base)
        base_display = int(base) if base.is_integer() else base
        number_display = int(number) if number.is_integer() else number
        print(f"log_{base_display}({number_display}) = {result:.6f}")
        return f"print(math.log({number}) / math.log({base}))"
    
    def _absolute_value(self, match):
        """Calculate absolute value"""
        number = float(match.group(1))
        result = abs(number)
        number_display = int(number) if number.is_integer() else number
        result_display = int(result) if result.is_integer() else result
        print(f"|{number_display}| = {result_display}")
        return f"print(abs({number}))"
    
    def _factorial(self, match):
        """Calculate factorial"""
        number = int(match.group(1))
        if number < 0:
            print("Error: Cannot calculate factorial of negative number!")
            return None
        if number > 100:
            print("Error: Number too large for factorial calculation!")
            return None
        result = math.factorial(number)
        print(f"{number}! = {result}")
        return f"print(math.factorial({number}))"
    
    def _make_uppercase(self, match):
        """Convert string to uppercase"""
        text = match.group(1)
        result = text.upper()
        print(f"'{text}' in uppercase: '{result}'")
        return f'print("{text}".upper())'
    
    def _make_lowercase(self, match):
        """Convert string to lowercase"""
        text = match.group(1)
        result = text.lower()
        print(f"'{text}' in lowercase: '{result}'")
        return f'print("{text}".lower())'
    
    def _string_length(self, match):
        """Get length of string"""
        text = match.group(1)
        result = len(text)
        print(f"Length of '{text}': {result}")
        return f'print(len("{text}"))'
    
    def _reverse_string(self, match):
        """Reverse a string"""
        text = match.group(1)
        result = text[::-1]
        print(f"'{text}' reversed: '{result}'")
        return f'print("{text}"[::-1])'
    
    def _replace_string(self, match):
        """Replace text in string"""
        old_text, new_text, source = match.group(1), match.group(2), match.group(3)
        result = source.replace(old_text, new_text)
        print(f"Replaced '{old_text}' with '{new_text}' in '{source}': '{result}'")
        return f'print("{source}".replace("{old_text}", "{new_text}"))'
    
    def _split_string(self, match):
        """Split string by delimiter"""
        text, delimiter = match.group(1), match.group(2)
        result = text.split(delimiter)
        print(f"Split '{text}' by '{delimiter}': {result}")
        return f'print("{text}".split("{delimiter}"))'
    
    def _get_current_time(self, match):
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        print(f"Current time: {time_str}")
        return "print(datetime.datetime.now().strftime('%H:%M:%S'))"
    
    def _get_current_date(self, match):
        """Get current date"""
        today = datetime.date.today()
        date_str = today.strftime("%Y-%m-%d")
        print(f"Current date: {date_str}")
        return "print(datetime.date.today().strftime('%Y-%m-%d'))"
    
    def _get_current_datetime(self, match):
        """Get current datetime"""
        now = datetime.datetime.now()
        datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Current datetime: {datetime_str}")
        return "print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))"
    
    def _add_days_to_today(self, match):
        """Add days to current date"""
        days = int(match.group(1))
        future_date = datetime.date.today() + datetime.timedelta(days=days)
        date_str = future_date.strftime("%Y-%m-%d")
        print(f"Date {days} days from today: {date_str}")
        return f"print((datetime.date.today() + datetime.timedelta(days={days})).strftime('%Y-%m-%d'))"
    
    def _subtract_days_from_today(self, match):
        """Subtract days from current date"""
        days = int(match.group(1))
        past_date = datetime.date.today() - datetime.timedelta(days=days)
        date_str = past_date.strftime("%Y-%m-%d")
        print(f"Date {days} days ago: {date_str}")
        return f"print((datetime.date.today() - datetime.timedelta(days={days})).strftime('%Y-%m-%d'))"
    
    def _set_string_variable(self, match):
        """Set a string variable"""
        var_name, value = match.group(1), match.group(2)
        self.variables[var_name] = value
        print(f"Variable '{var_name}' set to '{value}'")
        return f'{var_name} = "{value}"'
    
    def _set_number_variable(self, match):
        """Set a number variable"""
        var_name, value_str = match.group(1), match.group(2)
        # Convert to float if contains decimal, otherwise int
        if '.' in value_str:
            value = float(value_str)
        else:
            value = int(value_str)
        self.variables[var_name] = value
        print(f"Variable '{var_name}' set to {value}")
        return f'{var_name} = {value}'
    
    def _create_variable(self, match):
        """Create a variable with any value"""
        var_name, value = match.group(1), match.group(2)
        # Try to parse as number, otherwise treat as string
        try:
            numeric_value = int(value)
            self.variables[var_name] = numeric_value
            print(f"Variable '{var_name}' created with value {numeric_value}")
            return f'{var_name} = {numeric_value}'
        except ValueError:
            # Remove quotes if present
            string_value = value.strip('\'"')
            self.variables[var_name] = string_value
            print(f"Variable '{var_name}' created with value '{string_value}'")
            return f'{var_name} = "{string_value}"'
    
    def _check_variable_type(self, match):
        """Check the type of a variable"""
        var_name = match.group(1)
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' does not exist!")
            return None
        
        value = self.variables[var_name]
        if isinstance(value, int):
            type_name = "integer"
        elif isinstance(value, float):
            type_name = "float"
        elif isinstance(value, str):
            type_name = "string"
        elif isinstance(value, bool):
            type_name = "boolean"
        elif isinstance(value, list):
            type_name = "list"
        else:
            type_name = type(value).__name__
        
        print(f"Variable '{var_name}' is of type: {type_name}")
        return f"type({var_name})"
    
    def _is_string_type(self, match):
        """Check if variable is a string"""
        var_name = match.group(1)
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' does not exist!")
            return None
        
        is_string = isinstance(self.variables[var_name], str)
        print(f"Variable '{var_name}' is {'a string' if is_string else 'not a string'}")
        return f"isinstance({var_name}, str)"
    
    def _is_number_type(self, match):
        """Check if variable is a number"""
        var_name = match.group(1)
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' does not exist!")
            return None
        
        is_number = isinstance(self.variables[var_name], (int, float))
        print(f"Variable '{var_name}' is {'a number' if is_number else 'not a number'}")
        return f"isinstance({var_name}, (int, float))"
    
    def _is_boolean_type(self, match):
        """Check if variable is a boolean"""
        var_name = match.group(1)
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' does not exist!")
            return None
        
        is_boolean = isinstance(self.variables[var_name], bool)
        print(f"Variable '{var_name}' is {'a boolean' if is_boolean else 'not a boolean'}")
        return f"isinstance({var_name}, bool)"
    
    def _convert_to_string(self, match):
        """Convert variable to string"""
        var_name = match.group(1)
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' does not exist!")
            return None
        
        old_value = self.variables[var_name]
        self.variables[var_name] = str(old_value)
        print(f"Variable '{var_name}' converted from {type(old_value).__name__} to string: '{self.variables[var_name]}'")
        return f"{var_name} = str({var_name})"
    
    def _convert_to_number(self, match):
        """Convert variable to number"""
        var_name = match.group(1)
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' does not exist!")
            return None
        
        old_value = self.variables[var_name]
        try:
            # Try int first, then float
            if isinstance(old_value, str):
                if '.' in old_value:
                    new_value = float(old_value)
                else:
                    new_value = int(old_value)
            else:
                new_value = float(old_value) if isinstance(old_value, bool) else old_value
            
            self.variables[var_name] = new_value
            print(f"Variable '{var_name}' converted to number: {new_value}")
            return f"{var_name} = {type(new_value).__name__}({var_name})"
        except ValueError:
            print(f"Error: Cannot convert '{old_value}' to a number!")
            return None
    
    def _convert_to_boolean(self, match):
        """Convert variable to boolean"""
        var_name = match.group(1)
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' does not exist!")
            return None
        
        old_value = self.variables[var_name]
        if isinstance(old_value, str):
            # Convert string to boolean
            if old_value.lower() in ['true', 'yes', '1', 'on']:
                new_value = True
            elif old_value.lower() in ['false', 'no', '0', 'off', '']:
                new_value = False
            else:
                new_value = bool(old_value)  # Non-empty strings are True
        else:
            new_value = bool(old_value)
        
        self.variables[var_name] = new_value
        print(f"Variable '{var_name}' converted to boolean: {new_value}")
        return f"{var_name} = bool({var_name})"
    
    def _create_list(self, match):
        """Create a named list"""
        list_name, values_str = match.group(1), match.group(2)
        # Parse comma-separated values
        values = [v.strip().strip('\'"') for v in values_str.split(',')]
        # Try to convert to numbers where possible
        parsed_values = []
        for v in values:
            try:
                parsed_values.append(int(v))
            except ValueError:
                parsed_values.append(v)
        
        self.lists[list_name] = parsed_values
        print(f"List '{list_name}' created with values: {parsed_values}")
        return f"{list_name} = {parsed_values}"
    
    def _create_anonymous_list(self, match):
        """Create the current working list"""
        values_str = match.group(1)
        values = [v.strip().strip('\'"') for v in values_str.split(',')]
        parsed_values = []
        for v in values:
            try:
                parsed_values.append(int(v))
            except ValueError:
                parsed_values.append(v)
        
        self.current_list = parsed_values
        print(f"List created with values: {parsed_values}")
        return f"current_list = {parsed_values}"
    
    def _add_to_list(self, match):
        """Add item to named list"""
        value, list_name = match.group(1).strip().strip('\'"'), match.group(2)
        if list_name not in self.lists:
            print(f"Error: List '{list_name}' doesn't exist!")
            return None
        
        # Try to convert to number
        try:
            value = int(value)
        except ValueError:
            pass
        
        self.lists[list_name].append(value)
        print(f"Added {value} to list '{list_name}'. List is now: {self.lists[list_name]}")
        return f"{list_name}.append({repr(value)})"
    
    def _add_to_anonymous_list(self, match):
        """Add item to current list"""
        value = match.group(1).strip().strip('\'"')
        try:
            value = int(value)
        except ValueError:
            pass
        
        self.current_list.append(value)
        print(f"Added {value} to list. List is now: {self.current_list}")
        return f"current_list.append({repr(value)})"
    
    def _show_list(self, match):
        """Show named list"""
        list_name = match.group(1)
        if list_name not in self.lists:
            print(f"Error: List '{list_name}' doesn't exist!")
            return None
        
        print(f"List '{list_name}': {self.lists[list_name]}")
        return f"print({list_name})"
    
    def _show_anonymous_list(self, match):
        """Show current list"""
        print(f"Current list: {self.current_list}")
        return "print(current_list)"
    
    def _save_to_file(self, match):
        """Save text to a file"""
        text, filename = match.group(1), match.group(2)
        try:
            with open(filename, 'w') as f:
                f.write(text)
            print(f"Saved text to '{filename}'")
            return f'with open("{filename}", "w") as f: f.write("{text}")'
        except Exception as e:
            print(f"Error saving to file: {e}")
            return None
    
    def _read_file(self, match):
        """Read contents of a file"""
        filename = match.group(1)
        try:
            with open(filename, 'r') as f:
                content = f.read()
            print(f"Contents of '{filename}':")
            print(content)
            return f'with open("{filename}", "r") as f: print(f.read())'
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found!")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def _create_csv(self, match):
        """Create a CSV file with headers"""
        filename, headers_str = match.group(1), match.group(2)
        headers = [h.strip().strip('\'"') for h in headers_str.split(',')]
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"Created CSV file '{filename}' with headers: {headers}")
            return f'csv.writer(open("{filename}", "w")).writerow({headers})'
        except Exception as e:
            print(f"Error creating CSV: {e}")
            return None
    
    def _add_csv_row(self, match):
        """Add row to CSV file"""
        row_str, filename = match.group(1), match.group(2)
        row = [r.strip().strip('\'"') for r in row_str.split(',')]
        try:
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            print(f"Added row {row} to '{filename}'")
            return f'csv.writer(open("{filename}", "a")).writerow({row})'
        except Exception as e:
            print(f"Error adding to CSV: {e}")
            return None
    
    def _read_csv(self, match):
        """Read CSV file"""
        filename = match.group(1)
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            print(f"Contents of CSV '{filename}':")
            for i, row in enumerate(rows):
                print(f"  Row {i+1}: {row}")
            return f'print(list(csv.reader(open("{filename}", "r"))))'
        except FileNotFoundError:
            print(f"Error: CSV file '{filename}' not found!")
            return None
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return None
    
    def _save_list_to_json(self, match):
        """Save list to JSON file"""
        list_name, filename = match.group(1), match.group(2)
        if list_name not in self.lists:
            print(f"Error: List '{list_name}' doesn't exist!")
            return None
        try:
            with open(filename, 'w') as f:
                json.dump(self.lists[list_name], f, indent=2)
            print(f"Saved list '{list_name}' to '{filename}'")
            return f'json.dump({list_name}, open("{filename}", "w"))'
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return None
    
    def _load_list_from_json(self, match):
        """Load list from JSON file"""
        filename = match.group(1)
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.current_list = data
            print(f"Loaded list from '{filename}': {data}")
            return f'json.load(open("{filename}", "r"))'
        except FileNotFoundError:
            print(f"Error: JSON file '{filename}' not found!")
            return None
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None
    
    def _check_file_exists(self, match):
        """Check if a file exists"""
        filename = match.group(1)
        exists = os.path.exists(filename)
        print(f"File '{filename}' {'exists' if exists else 'does not exist'}")
        return f'os.path.exists("{filename}")'
    
    def _delete_file(self, match):
        """Delete a file"""
        filename = match.group(1)
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"File '{filename}' deleted successfully")
                return f'os.remove("{filename}")'
            else:
                print(f"Error: File '{filename}' does not exist!")
                return None
        except Exception as e:
            print(f"Error deleting file: {e}")
            return None
    
    def _copy_file(self, match):
        """Copy a file to another location"""
        source, destination = match.group(1), match.group(2)
        try:
            if not os.path.exists(source):
                print(f"Error: Source file '{source}' does not exist!")
                return None
            
            import shutil
            shutil.copy2(source, destination)
            print(f"File copied from '{source}' to '{destination}'")
            return f'shutil.copy2("{source}", "{destination}")'
        except Exception as e:
            print(f"Error copying file: {e}")
            return None
    
    def _save_to_xml(self, match):
        """Save variables to XML file"""
        filename = match.group(1)
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.Element("vernacular_data")
            
            # Add variables
            vars_elem = ET.SubElement(root, "variables")
            for name, value in self.variables.items():
                var_elem = ET.SubElement(vars_elem, "variable")
                var_elem.set("name", name)
                var_elem.set("type", type(value).__name__)
                var_elem.text = str(value)
            
            # Add lists
            lists_elem = ET.SubElement(root, "lists")
            for name, items in self.lists.items():
                list_elem = ET.SubElement(lists_elem, "list")
                list_elem.set("name", name)
                for item in items:
                    item_elem = ET.SubElement(list_elem, "item")
                    item_elem.text = str(item)
            
            # Write to file
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            
            print(f"Data saved to XML file '{filename}'")
            print(f"Saved: {len(self.variables)} variables, {len(self.lists)} lists")
            return f'ET.ElementTree(root).write("{filename}")'
        except Exception as e:
            print(f"Error saving to XML: {e}")
            return None
    
    def _load_from_xml(self, match):
        """Load variables from XML file"""
        filename = match.group(1)
        try:
            if not os.path.exists(filename):
                print(f"Error: XML file '{filename}' does not exist!")
                return None
            
            import xml.etree.ElementTree as ET
            tree = ET.parse(filename)
            root = tree.getroot()
            
            # Clear current variables and lists
            self.variables.clear()
            self.lists.clear()
            
            # Load variables
            vars_elem = root.find("variables")
            if vars_elem is not None:
                for var_elem in vars_elem.findall("variable"):
                    name = var_elem.get("name")
                    var_type = var_elem.get("type")
                    value_str = var_elem.text or ""
                    
                    # Convert based on type
                    if var_type == "int":
                        value = int(value_str)
                    elif var_type == "float":
                        value = float(value_str)
                    elif var_type == "bool":
                        value = value_str.lower() == "true"
                    else:
                        value = value_str
                    
                    self.variables[name] = value
            
            # Load lists
            lists_elem = root.find("lists")
            if lists_elem is not None:
                for list_elem in lists_elem.findall("list"):
                    name = list_elem.get("name")
                    items = []
                    for item_elem in list_elem.findall("item"):
                        items.append(item_elem.text or "")
                    self.lists[name] = items
            
            print(f"Data loaded from XML file '{filename}'")
            print(f"Loaded: {len(self.variables)} variables, {len(self.lists)} lists")
            return f'ET.parse("{filename}")'
        except Exception as e:
            print(f"Error loading from XML: {e}")
            return None
    
    def _save_to_yaml(self, match):
        """Save variables to YAML file"""
        filename = match.group(1)
        try:
            # Try to import yaml, provide helpful error if not available
            try:
                import yaml
            except ImportError:
                print("Error: PyYAML library not installed. Install with: pip install PyYAML")
                return None
            
            data = {
                'variables': self.variables,
                'lists': self.lists
            }
            
            with open(filename, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=True)
            
            print(f"Data saved to YAML file '{filename}'")
            print(f"Saved: {len(self.variables)} variables, {len(self.lists)} lists")
            return f'yaml.dump(data, open("{filename}", "w"))'
        except Exception as e:
            print(f"Error saving to YAML: {e}")
            return None
    
    def _load_from_yaml(self, match):
        """Load variables from YAML file"""
        filename = match.group(1)
        try:
            if not os.path.exists(filename):
                print(f"Error: YAML file '{filename}' does not exist!")
                return None
            
            try:
                import yaml
            except ImportError:
                print("Error: PyYAML library not installed. Install with: pip install PyYAML")
                return None
            
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)
            
            # Clear current state
            self.variables.clear()
            self.lists.clear()
            
            # Load data
            if 'variables' in data:
                self.variables.update(data['variables'])
            if 'lists' in data:
                self.lists.update(data['lists'])
            
            print(f"Data loaded from YAML file '{filename}'")
            print(f"Loaded: {len(self.variables)} variables, {len(self.lists)} lists")
            return f'yaml.safe_load(open("{filename}", "r"))'
        except Exception as e:
            print(f"Error loading from YAML: {e}")
            return None
    
    def _get_user_input(self, match):
        """Get input from user"""
        prompt = match.group(1)
        try:
            user_input = input(f"Please enter {prompt}: ")
            print(f"You entered: {user_input}")
            # Store in a default variable
            self.variables['user_input'] = user_input
            return f'input("Please enter {prompt}: ")'
        except KeyboardInterrupt:
            print("\nInput cancelled")
            return None
    
    def _if_equals(self, match):
        """Enhanced if statement for equality"""
        var_name, value, action = match.group(1), match.group(2), match.group(3)
        
        if var_name in self.variables:
            # Try to convert value to match variable type
            var_val = self.variables[var_name]
            try:
                if isinstance(var_val, int):
                    compare_val = int(value.strip('\'"'))
                else:
                    compare_val = value.strip('\'"')
            except ValueError:
                compare_val = value.strip('\'"')
            
            if var_val == compare_val:
                print(f"Condition met: {var_name} equals {compare_val}")
                self.process_command(action)
            else:
                print(f"Condition not met: {var_name} ({var_val}) does not equal {compare_val}")
            return f'if {var_name} == {repr(compare_val)}: {action}'
        else:
            print(f"Error: Variable '{var_name}' doesn't exist!")
            return None
    
    def _if_greater_than(self, match):
        """If statement for greater than comparison"""
        var_name, threshold, action = match.group(1), int(match.group(2)), match.group(3)
        
        if var_name in self.variables and isinstance(self.variables[var_name], (int, float)):
            if self.variables[var_name] > threshold:
                print(f"Condition met: {var_name} ({self.variables[var_name]}) > {threshold}")
                self.process_command(action)
            else:
                print(f"Condition not met: {var_name} ({self.variables[var_name]}) <= {threshold}")
            return f'if {var_name} > {threshold}: {action}'
        else:
            print(f"Error: Variable '{var_name}' doesn't exist or isn't a number!")
            return None
    
    def _if_less_than(self, match):
        """If statement for less than comparison"""
        var_name, threshold, action = match.group(1), int(match.group(2)), match.group(3)
        
        if var_name in self.variables and isinstance(self.variables[var_name], (int, float)):
            if self.variables[var_name] < threshold:
                print(f"Condition met: {var_name} ({self.variables[var_name]}) < {threshold}")
                self.process_command(action)
            else:
                print(f"Condition not met: {var_name} ({self.variables[var_name]}) >= {threshold}")
            return f'if {var_name} < {threshold}: {action}'
        else:
            print(f"Error: Variable '{var_name}' doesn't exist or isn't a number!")
            return None
    
    def _if_contains(self, match):
        """If statement for string contains"""
        var_name, search_text, action = match.group(1), match.group(2), match.group(3)
        
        if var_name in self.variables and isinstance(self.variables[var_name], str):
            if search_text in self.variables[var_name]:
                print(f"Condition met: '{var_name}' contains '{search_text}'")
                self.process_command(action)
            else:
                print(f"Condition not met: '{var_name}' does not contain '{search_text}'")
            return f'if "{search_text}" in {var_name}: {action}'
        else:
            print(f"Error: Variable '{var_name}' doesn't exist or isn't a string!")
            return None
    
    def _if_list_size(self, match):
        """If statement for list size"""
        list_name, size, action = match.group(1), int(match.group(2)), match.group(3)
        
        if list_name in self.lists:
            if len(self.lists[list_name]) == size:
                print(f"Condition met: list '{list_name}' has {size} items")
                self.process_command(action)
            else:
                print(f"Condition not met: list '{list_name}' has {len(self.lists[list_name])} items, not {size}")
            return f'if len({list_name}) == {size}: {action}'
        else:
            print(f"Error: List '{list_name}' doesn't exist!")
            return None
    
    def _if_and_greater(self, match):
        """Handle AND conditions for greater than"""
        var1, thresh1, var2, thresh2, action = match.group(1), int(match.group(2)), match.group(3), int(match.group(4)), match.group(5)
        
        if var1 in self.variables and var2 in self.variables:
            val1, val2 = self.variables[var1], self.variables[var2]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 > thresh1 and val2 > thresh2:
                    print(f"Condition met: {var1} ({val1}) > {thresh1} AND {var2} ({val2}) > {thresh2}")
                    self.process_command(action)
                else:
                    print(f"Condition not met: {var1} ({val1}) > {thresh1} AND {var2} ({val2}) > {thresh2}")
                return f'if {var1} > {thresh1} and {var2} > {thresh2}: {action}'
        print(f"Error: Variables must exist and be numbers!")
        return None
    
    def _if_and_less(self, match):
        """Handle AND conditions for less than"""
        var1, thresh1, var2, thresh2, action = match.group(1), int(match.group(2)), match.group(3), int(match.group(4)), match.group(5)
        
        if var1 in self.variables and var2 in self.variables:
            val1, val2 = self.variables[var1], self.variables[var2]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 < thresh1 and val2 < thresh2:
                    print(f"Condition met: {var1} ({val1}) < {thresh1} AND {var2} ({val2}) < {thresh2}")
                    self.process_command(action)
                else:
                    print(f"Condition not met: {var1} ({val1}) < {thresh1} AND {var2} ({val2}) < {thresh2}")
                return f'if {var1} < {thresh1} and {var2} < {thresh2}: {action}'
        print(f"Error: Variables must exist and be numbers!")
        return None
    
    def _if_and_equals(self, match):
        """Handle AND conditions for equality"""
        var1, val1, var2, val2, action = match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)
        
        if var1 in self.variables and var2 in self.variables:
            if self.variables[var1] == val1 and self.variables[var2] == val2:
                print(f"Condition met: {var1} equals '{val1}' AND {var2} equals '{val2}'")
                self.process_command(action)
            else:
                print(f"Condition not met: {var1} equals '{val1}' AND {var2} equals '{val2}'")
            return f'if {var1} == "{val1}" and {var2} == "{val2}": {action}'
        print(f"Error: Variables '{var1}' or '{var2}' don't exist!")
        return None
    
    def _if_or_greater(self, match):
        """Handle OR conditions for greater than"""
        var1, thresh1, var2, thresh2, action = match.group(1), int(match.group(2)), match.group(3), int(match.group(4)), match.group(5)
        
        if var1 in self.variables and var2 in self.variables:
            val1, val2 = self.variables[var1], self.variables[var2]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 > thresh1 or val2 > thresh2:
                    print(f"Condition met: {var1} ({val1}) > {thresh1} OR {var2} ({val2}) > {thresh2}")
                    self.process_command(action)
                else:
                    print(f"Condition not met: {var1} ({val1}) > {thresh1} OR {var2} ({val2}) > {thresh2}")
                return f'if {var1} > {thresh1} or {var2} > {thresh2}: {action}'
        print(f"Error: Variables must exist and be numbers!")
        return None
    
    def _if_or_less(self, match):
        """Handle OR conditions for less than"""
        var1, thresh1, var2, thresh2, action = match.group(1), int(match.group(2)), match.group(3), int(match.group(4)), match.group(5)
        
        if var1 in self.variables and var2 in self.variables:
            val1, val2 = self.variables[var1], self.variables[var2]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 < thresh1 or val2 < thresh2:
                    print(f"Condition met: {var1} ({val1}) < {thresh1} OR {var2} ({val2}) < {thresh2}")
                    self.process_command(action)
                else:
                    print(f"Condition not met: {var1} ({val1}) < {thresh1} OR {var2} ({val2}) < {thresh2}")
                return f'if {var1} < {thresh1} or {var2} < {thresh2}: {action}'
        print(f"Error: Variables must exist and be numbers!")
        return None
    
    def _if_or_equals(self, match):
        """Handle OR conditions for equality"""
        var1, val1, var2, val2, action = match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)
        
        if var1 in self.variables and var2 in self.variables:
            if self.variables[var1] == val1 or self.variables[var2] == val2:
                print(f"Condition met: {var1} equals '{val1}' OR {var2} equals '{val2}'")
                self.process_command(action)
            else:
                print(f"Condition not met: {var1} equals '{val1}' OR {var2} equals '{val2}'")
            return f'if {var1} == "{val1}" or {var2} == "{val2}": {action}'
        print(f"Error: Variables '{var1}' or '{var2}' don't exist!")
        return None
    
    def _if_not_equals(self, match):
        """Handle NOT conditions for equality"""
        if len(match.groups()) == 3:  # "if not var equals value then action"
            var_name, value, action = match.group(1), match.group(2), match.group(3)
        else:  # "if var is not equal to value then action"
            var_name, value, action = match.group(1), match.group(2), match.group(3)
            
        if var_name in self.variables:
            if self.variables[var_name] != value:
                print(f"Condition met: {var_name} does NOT equal '{value}'")
                self.process_command(action)
            else:
                print(f"Condition not met: {var_name} equals '{value}'")
            return f'if {var_name} != "{value}": {action}'
        print(f"Error: Variable '{var_name}' doesn't exist!")
        return None
    
    def _if_not_greater(self, match):
        """Handle NOT conditions for greater than"""
        var_name, threshold, action = match.group(1), int(match.group(2)), match.group(3)
        
        if var_name in self.variables and isinstance(self.variables[var_name], (int, float)):
            if not (self.variables[var_name] > threshold):
                print(f"Condition met: {var_name} ({self.variables[var_name]}) is NOT > {threshold}")
                self.process_command(action)
            else:
                print(f"Condition not met: {var_name} ({self.variables[var_name]}) is > {threshold}")
            return f'if not {var_name} > {threshold}: {action}'
        print(f"Error: Variable '{var_name}' doesn't exist or isn't a number!")
        return None
    
    def _repeat_command(self, match):
        """Handle repeat loops"""
        times, command = int(match.group(1)), match.group(2).strip()
        print(f"Repeating '{command}' {times} times:")
        
        # Reset loop control flags
        self.break_loop = False
        self.continue_loop = False
        
        for i in range(times):
            if self.break_loop:
                print("Loop terminated by break")
                self.break_loop = False  # Reset flag
                break
                
            print(f"  {i+1}: ", end="")
            # Recursively process the sub-command
            self.process_command(command)
            
            if self.continue_loop:
                self.continue_loop = False  # Reset flag
                continue
        
        return f'for i in range({times}): {command}'
    
    def _foreach_list(self, match):
        """For each item in list"""
        list_name, action = match.group(1), match.group(2)
        
        if list_name not in self.lists:
            print(f"Error: List '{list_name}' doesn't exist!")
            if self.lists:
                available = ', '.join(list(self.lists.keys())[:5])
                print(f"Available lists: {available}")
                print(f"Tip: Create it first with 'create list {list_name} with item1, item2'")
            else:
                print("No lists exist yet. Create one with 'create list name with item1, item2'")
            return None
        
        print(f"For each item in list '{list_name}':")
        
        # Reset loop control flags
        self.break_loop = False
        self.continue_loop = False
        
        for i, item in enumerate(self.lists[list_name]):
            if self.break_loop:
                print("Loop terminated by break")
                self.break_loop = False  # Reset flag
                break
                
            print(f"  Item {i+1} ({item}): ", end="")
            # Set current item as a temporary variable
            old_item = self.variables.get('item')
            self.variables['item'] = item
            self.process_command(action)
            # Restore old item value
            if old_item is not None:
                self.variables['item'] = old_item
            elif 'item' in self.variables:
                del self.variables['item']
                
            if self.continue_loop:
                self.continue_loop = False  # Reset flag
                continue
        
        return f'for item in {list_name}: {action}'
    
    def _while_less_than(self, match):
        """Simple while loop"""
        var_name, limit, action = match.group(1), int(match.group(2)), match.group(3)
        
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' doesn't exist!")
            return None
        
        if not isinstance(self.variables[var_name], (int, float)):
            print(f"Error: Variable '{var_name}' must be a number!")
            return None
        
        print(f"While {var_name} < {limit}:")
        iterations = 0
        max_iterations = 100  # Safety limit
        
        # Reset loop control flags
        self.break_loop = False
        self.continue_loop = False
        
        while self.variables[var_name] < limit and iterations < max_iterations:
            if self.break_loop:
                print("Loop terminated by break")
                self.break_loop = False  # Reset flag
                break
                
            print(f"  {var_name} = {self.variables[var_name]}: ", end="")
            self.process_command(action)
            iterations += 1
            
            if self.continue_loop:
                self.continue_loop = False  # Reset flag
                continue
        
        if iterations >= max_iterations:
            print(f"Warning: Loop stopped after {max_iterations} iterations (safety limit)")
        
        return f'while {var_name} < {limit}: {action}'
    
    def _count_and_do(self, match):
        """Count from X to Y and do action"""
        start, end, action = int(match.group(1)), int(match.group(2)), match.group(3)
        
        print(f"Counting from {start} to {end}:")
        
        # Reset loop control flags
        self.break_loop = False
        self.continue_loop = False
        
        for i in range(start, end + 1):
            if self.break_loop:
                print("Loop terminated by break")
                self.break_loop = False  # Reset flag
                break
                
            print(f"  Count {i}: ", end="")
            # Set counter as temporary variable
            old_counter = self.variables.get('counter')
            self.variables['counter'] = i
            self.process_command(action)
            # Restore old counter
            if old_counter is not None:
                self.variables['counter'] = old_counter
            elif 'counter' in self.variables:
                del self.variables['counter']
                
            if self.continue_loop:
                self.continue_loop = False  # Reset flag
                continue
        
        return f'for counter in range({start}, {end + 1}): {action}'
    
    def _break_loop(self, match):
        """Set break flag to exit current loop"""
        self.break_loop = True
        print("Breaking from loop...")
        return "break"
    
    def _continue_loop(self, match):
        """Set continue flag to skip to next iteration"""
        self.continue_loop = True
        print("Continuing to next iteration...")
        return "continue"
    
    def _define_function(self, match):
        """Define a simple function"""
        func_name, commands = match.group(1), match.group(2)
        self.functions[func_name] = commands
        print(f"Function '{func_name}' defined as: {commands}")
        return f'def {func_name}(): {commands}'
    
    def _call_function(self, match):
        """Call a user-defined function"""
        func_name = match.group(1)
        
        if func_name not in self.functions:
            print(f"Error: Function '{func_name}' is not defined!")
            if self.functions:
                available = ', '.join(list(self.functions.keys())[:5])
                print(f"Available functions: {available}")
                print(f"Tip: Define it first with 'define function {func_name} as action'")
            else:
                print("No functions exist yet. Create one with 'define function name as action'")
            return None
        
        print(f"Calling function '{func_name}':")
        self.process_command(self.functions[func_name])
        return f'{func_name}()'
    
    def _clear_screen(self, match):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Screen cleared.")
        return "os.system('clear')"
    
    def _list_variables(self, match):
        """List all variables"""
        if not self.variables:
            print("No variables defined.")
        else:
            print("Variables:")
            for name, value in self.variables.items():
                print(f"  {name} = {repr(value)}")
        return "print(variables)"
    
    def _list_lists(self, match):
        """List all lists"""
        if not self.lists:
            print("No lists defined.")
        else:
            print("Lists:")
            for name, value in self.lists.items():
                print(f"  {name} = {value}")
        return "print(lists)"
    
    def _delete_variable(self, match):
        """Delete a variable"""
        var_name = match.group(1)
        if var_name in self.variables:
            del self.variables[var_name]
            print(f"Variable '{var_name}' deleted.")
            return f"del {var_name}"
        else:
            print(f"Error: Variable '{var_name}' doesn't exist!")
            return None
    
    def _delete_list(self, match):
        """Delete a list"""
        list_name = match.group(1)
        if list_name in self.lists:
            del self.lists[list_name]
            print(f"List '{list_name}' deleted.")
            return f"del {list_name}"
        else:
            print(f"Error: List '{list_name}' doesn't exist!")
            return None
    
    def _reset_all(self, match):
        """Reset all variables, lists, and functions"""
        self.variables.clear()
        self.lists.clear()
        self.functions.clear()
        self.current_list.clear()
        print("All variables, lists, and functions have been reset.")
        return "reset_all()"
    
    def _save_session(self, match):
        """Save current session state to a file"""
        filename = match.group(1)
        try:
            session_data = {
                'variables': self.variables,
                'lists': self.lists,
                'functions': self.functions,
                'current_list': self.current_list
            }
            
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"Session saved to '{filename}'")
            print(f"Saved: {len(self.variables)} variables, {len(self.lists)} lists, {len(self.functions)} functions")
            return f'json.dump(session_data, open("{filename}", "w"))'
        except Exception as e:
            print(f"Error saving session: {e}")
            return None
    
    def _load_session(self, match):
        """Load session state from a file"""
        filename = match.group(1)
        try:
            if not os.path.exists(filename):
                print(f"Error: Session file '{filename}' does not exist!")
                return None
            
            with open(filename, 'r') as f:
                session_data = json.load(f)
            
            # Clear current state
            self.variables.clear()
            self.lists.clear()
            self.functions.clear()
            self.current_list.clear()
            
            # Load saved state
            self.variables.update(session_data.get('variables', {}))
            self.lists.update(session_data.get('lists', {}))
            self.functions.update(session_data.get('functions', {}))
            self.current_list = session_data.get('current_list', [])
            
            print(f"Session loaded from '{filename}'")
            print(f"Loaded: {len(self.variables)} variables, {len(self.lists)} lists, {len(self.functions)} functions")
            return f'json.load(open("{filename}", "r"))'
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def _simple_if(self, match):
        """Handle simple if statements"""
        var1, var2, message = match.group(1), match.group(2), match.group(3)
        
        # Check if variables exist
        if var1 in self.variables and var2 in self.variables:
            if self.variables[var1] == self.variables[var2]:
                print(message)
            return f'if {var1} == {var2}: print("{message}")'
        else:
            print(f"Error: Unknown variable(s). Available: {list(self.variables.keys())}")
            return None
    
    def _show_help(self, match):
        """Show available commands"""
        help_text = """
Available commands:

📝 BASIC OUTPUT:
- print "hello world" or display "message"
- print variableName (print variable values)
- display the value of variableName

🧮 MATH OPERATIONS (supports decimals and negative numbers):
- add 5 and 3, add 2.5 and -1.5
- subtract 2 from 10  
- multiply 4 by 6
- divide 10 by 2
- calculate the square root of 16
- raise 2 to the power of 3
- generate a random number between 1 and 100
- find the minimum of 5, 2, 8, 1
- find the maximum of 5, 2, 8, 1
- calculate the average of 5, 2, 8, 1
- round 3.14159 to 2 decimal places

🔬 ADVANCED MATH:
- calculate the sine of 30
- calculate the cosine of 45
- calculate the tangent of 60
- calculate the natural log of 10
- calculate the log base 2 of 8
- calculate the absolute value of -15
- calculate the factorial of 5

📊 VARIABLES:
- set myvar to "hello" or set num to 42
- create variable name with value 100

📋 LISTS:
- create list mylist with 1, 2, 3
- create a list with apple, banana, cherry
- add 4 to list mylist
- add orange to the list
- show list mylist
- show the list

🔤 STRING OPERATIONS:
- make "hello world" uppercase
- make "HELLO WORLD" lowercase
- get the length of "hello"
- reverse "hello"
- replace "old" with "new" in "hello old world"
- split "apple,banana,cherry" by ","

📅 DATE & TIME:
- get the current time
- get the current date
- get the current datetime
- add 7 days to today
- subtract 3 days from today

📁 FILE OPERATIONS:
- save "hello world" to file.txt
- write "some text" to data.txt
- read the contents of file.txt
- create a CSV file data.csv with headers name, age, city
- add row John, 25, NYC to CSV data.csv
- read the CSV file data.csv
- save list mylist to data.json
- load list from data.json

💬 INPUT/OUTPUT:
- ask the user for their name
- get input for age
- prompt for favorite color

🔄 LOOPS:
- repeat 5 times: print "hello"
- for each item in list mylist do print item
- while counter is less than 10 do add 1 to counter
- count from 1 to 5 and print counter

🤔 CONDITIONALS:
- if name equals "John" then print "Hello John"
- if age is greater than 18 then print "Adult"
- if age is less than 13 then print "Child"
- if message contains "hello" then print "Greeting found"
- if list mylist has 5 items then print "List is full"

⚡ FUNCTIONS:
- define function greet as print "Hello there"
- call function greet
- run greet

🔧 SYSTEM:
- clear the screen
- list all variables
- list all lists
- delete variable myvar
- delete list mylist
- reset everything

❓ HELP:
- help (show this message)
        """
        print(help_text.strip())
        return "help()"
    
    def _benchmark_command(self, match):
        """Run performance benchmark"""
        results = self.benchmark_performance(iterations=500)
        return f"benchmark_performance()"
    
    def _create_database(self, match):
        """Create a new SQLite database"""
        db_name = match.group(1)
        if not db_name.endswith('.db'):
            db_name += '.db'
        
        try:
            # Close existing connection if any
            if self.db_connection:
                self.db_connection.close()
            
            self.db_connection = sqlite3.connect(db_name)
            self.db_cursor = self.db_connection.cursor()
            print(f"Database '{db_name}' created and connected successfully")
            return f"sqlite3.connect('{db_name}')"
        except Exception as e:
            print(f"Error creating database: {e}")
            return None
    
    def _connect_database(self, match):
        """Connect to an existing SQLite database"""
        db_name = match.group(1)
        if not db_name.endswith('.db'):
            db_name += '.db'
        
        try:
            # Close existing connection if any
            if self.db_connection:
                self.db_connection.close()
            
            self.db_connection = sqlite3.connect(db_name)
            self.db_cursor = self.db_connection.cursor()
            print(f"Connected to database '{db_name}' successfully")
            return f"sqlite3.connect('{db_name}')"
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def _create_table(self, match):
        """Create a database table with specified columns"""
        if not self._check_db_connection():
            return None
        
        table_name, columns_str = match.group(1), match.group(2)
        
        # Parse column definitions (simple format: name type, name type)
        columns = []
        for column_def in columns_str.split(','):
            column_def = column_def.strip()
            if ' ' in column_def:
                name, col_type = column_def.split(None, 1)
                columns.append(f"{name} {col_type.upper()}")
            else:
                columns.append(f"{column_def} TEXT")  # Default to TEXT
        
        columns_sql = ', '.join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        
        try:
            self.db_cursor.execute(sql)
            self.db_connection.commit()
            print(f"Table '{table_name}' created with columns: {columns_sql}")
            return f"cursor.execute('{sql}')"
        except Exception as e:
            print(f"Error creating table: {e}")
            return None
    
    def _insert_into_table(self, match):
        """Insert values into a database table"""
        if not self._check_db_connection():
            return None
        
        table_name, values_str = match.group(1), match.group(2)
        
        # Parse values (simple comma-separated format)
        values = []
        for value in values_str.split(','):
            value = value.strip().strip('\'"')
            # Try to convert to number, otherwise keep as string
            try:
                if '.' in value:
                    values.append(float(value))
                else:
                    values.append(int(value))
            except ValueError:
                values.append(value)
        
        placeholders = ', '.join(['?' for _ in values])
        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        
        try:
            self.db_cursor.execute(sql, values)
            self.db_connection.commit()
            print(f"Inserted values {values} into table '{table_name}'")
            return f"cursor.execute('{sql}', {values})"
        except Exception as e:
            print(f"Error inserting into table: {e}")
            return None
    
    def _select_from_table(self, match):
        """Select specific columns from a database table"""
        if not self._check_db_connection():
            return None
        
        columns, table_name = match.group(1), match.group(2)
        sql = f"SELECT {columns} FROM {table_name}"
        
        try:
            self.db_cursor.execute(sql)
            results = self.db_cursor.fetchall()
            
            if results:
                print(f"Results from table '{table_name}':")
                for i, row in enumerate(results, 1):
                    print(f"  Row {i}: {row}")
            else:
                print(f"No results found in table '{table_name}'")
            
            return f"cursor.execute('{sql}').fetchall()"
        except Exception as e:
            print(f"Error selecting from table: {e}")
            return None
    
    def _select_all_from_table(self, match):
        """Select all columns from a database table"""
        if not self._check_db_connection():
            return None
        
        table_name = match.group(1)
        sql = f"SELECT * FROM {table_name}"
        
        try:
            self.db_cursor.execute(sql)
            results = self.db_cursor.fetchall()
            
            if results:
                print(f"All data from table '{table_name}':")
                for i, row in enumerate(results, 1):
                    print(f"  Row {i}: {row}")
            else:
                print(f"Table '{table_name}' is empty")
            
            return f"cursor.execute('{sql}').fetchall()"
        except Exception as e:
            print(f"Error selecting from table: {e}")
            return None
    
    def _update_table(self, match):
        """Update records in a database table"""
        if not self._check_db_connection():
            return None
        
        table_name, set_clause, where_clause = match.group(1), match.group(2), match.group(3)
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        
        try:
            self.db_cursor.execute(sql)
            self.db_connection.commit()
            updated_rows = self.db_cursor.rowcount
            print(f"Updated {updated_rows} row(s) in table '{table_name}'")
            return f"cursor.execute('{sql}')"
        except Exception as e:
            print(f"Error updating table: {e}")
            return None
    
    def _delete_from_table(self, match):
        """Delete records from a database table"""
        if not self._check_db_connection():
            return None
        
        table_name, where_clause = match.group(1), match.group(2)
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        
        try:
            self.db_cursor.execute(sql)
            self.db_connection.commit()
            deleted_rows = self.db_cursor.rowcount
            print(f"Deleted {deleted_rows} row(s) from table '{table_name}'")
            return f"cursor.execute('{sql}')"
        except Exception as e:
            print(f"Error deleting from table: {e}")
            return None
    
    def _drop_table(self, match):
        """Drop a database table"""
        if not self._check_db_connection():
            return None
        
        table_name = match.group(1)
        sql = f"DROP TABLE IF EXISTS {table_name}"
        
        try:
            self.db_cursor.execute(sql)
            self.db_connection.commit()
            print(f"Table '{table_name}' dropped successfully")
            return f"cursor.execute('{sql}')"
        except Exception as e:
            print(f"Error dropping table: {e}")
            return None
    
    def _list_tables(self, match):
        """List all tables in the database"""
        if not self._check_db_connection():
            return None
        
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        
        try:
            self.db_cursor.execute(sql)
            tables = self.db_cursor.fetchall()
            
            if tables:
                print("Tables in database:")
                for table in tables:
                    print(f"  • {table[0]}")
            else:
                print("No tables found in database")
            
            return f"cursor.execute('{sql}').fetchall()"
        except Exception as e:
            print(f"Error listing tables: {e}")
            return None
    
    def _describe_table(self, match):
        """Describe the structure of a database table"""
        if not self._check_db_connection():
            return None
        
        table_name = match.group(1)
        sql = f"PRAGMA table_info({table_name})"
        
        try:
            self.db_cursor.execute(sql)
            columns = self.db_cursor.fetchall()
            
            if columns:
                print(f"Structure of table '{table_name}':")
                for col in columns:
                    col_id, name, col_type, not_null, default, pk = col
                    pk_indicator = " (PRIMARY KEY)" if pk else ""
                    null_indicator = " NOT NULL" if not_null else ""
                    default_indicator = f" DEFAULT {default}" if default else ""
                    print(f"  • {name}: {col_type}{null_indicator}{default_indicator}{pk_indicator}")
            else:
                print(f"Table '{table_name}' does not exist")
            
            return f"cursor.execute('{sql}').fetchall()"
        except Exception as e:
            print(f"Error describing table: {e}")
            return None
    
    def _close_database(self, match):
        """Close the database connection"""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None
            self.db_cursor = None
            print("Database connection closed")
            return "connection.close()"
        else:
            print("No database connection to close")
            return None
    
    def _check_db_connection(self):
        """Check if database is connected"""
        if not self.db_connection:
            print("Error: No database connection. Use 'create database \"name\"' or 'connect to database \"name\"' first")
            return False
        return True
    
    def _http_get(self, match):
        """Make an HTTP GET request to a URL"""
        url = match.group(1)
        
        try:
            print(f"Making GET request to: {url}")
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                status_code = response.getcode()
                content_type = response.headers.get('Content-Type', 'unknown')
                
                print(f"Status: {status_code}")
                print(f"Content-Type: {content_type}")
                print(f"Response length: {len(data)} characters")
                
                # Try to parse as JSON if it looks like JSON
                if 'application/json' in content_type or data.strip().startswith('{'):
                    try:
                        json_data = json.loads(data)
                        print("Response (JSON):")
                        print(json.dumps(json_data, indent=2)[:500] + "..." if len(str(json_data)) > 500 else json.dumps(json_data, indent=2))
                    except json.JSONDecodeError:
                        print("Response (text):")
                        print(data[:500] + "..." if len(data) > 500 else data)
                else:
                    print("Response (text):")
                    print(data[:500] + "..." if len(data) > 500 else data)
                
                return f"urllib.request.urlopen('{url}').read()"
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return None
        except Exception as e:
            print(f"Error making request: {e}")
            return None
    
    def _http_post(self, match):
        """Make an HTTP POST request with data"""
        url, data_str = match.group(1), match.group(2)
        
        try:
            # Parse data (simple key=value, key=value format)
            data_dict = {}
            if data_str:
                for pair in data_str.split(','):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        data_dict[key.strip()] = value.strip().strip('\'"')
            
            # Encode data
            data = urllib.parse.urlencode(data_dict).encode('utf-8')
            
            print(f"Making POST request to: {url}")
            print(f"Data: {data_dict}")
            
            req = urllib.request.Request(url, data=data, method='POST')
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                status_code = response.getcode()
                content_type = response.headers.get('Content-Type', 'unknown')
                
                print(f"Status: {status_code}")
                print(f"Content-Type: {content_type}")
                
                # Try to parse as JSON if it looks like JSON
                if 'application/json' in content_type or response_data.strip().startswith('{'):
                    try:
                        json_data = json.loads(response_data)
                        print("Response (JSON):")
                        print(json.dumps(json_data, indent=2)[:500] + "..." if len(str(json_data)) > 500 else json.dumps(json_data, indent=2))
                    except json.JSONDecodeError:
                        print("Response (text):")
                        print(response_data[:500] + "..." if len(response_data) > 500 else response_data)
                else:
                    print("Response (text):")
                    print(response_data[:500] + "..." if len(response_data) > 500 else response_data)
                
                return f"urllib.request.Request('{url}', data={data_dict})"
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return None
        except Exception as e:
            print(f"Error making POST request: {e}")
            return None
    
    def _download_file(self, match):
        """Download a file from a URL"""
        url, filename = match.group(1), match.group(2)
        
        try:
            print(f"Downloading from: {url}")
            print(f"Saving to: {filename}")
            
            urllib.request.urlretrieve(url, filename)
            
            # Check if file was created and get its size
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"Download completed successfully!")
                print(f"File size: {file_size} bytes")
            else:
                print("Download failed - file not created")
                return None
            
            return f"urllib.request.urlretrieve('{url}', '{filename}')"
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return None
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def _check_url(self, match):
        """Check if a URL is accessible"""
        url = match.group(1)
        
        try:
            print(f"Checking URL: {url}")
            with urllib.request.urlopen(url) as response:
                status_code = response.getcode()
                if status_code == 200:
                    print(f"✓ URL is accessible (Status: {status_code})")
                else:
                    print(f"⚠ URL responded with status: {status_code}")
                return f"urllib.request.urlopen('{url}').getcode() == 200"
        except urllib.error.HTTPError as e:
            print(f"✗ URL not accessible - HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"✗ URL not accessible - URL Error: {e.reason}")
            return None
        except Exception as e:
            print(f"✗ Error checking URL: {e}")
            return None
    
    def _get_url_status(self, match):
        """Get the HTTP status of a URL"""
        url = match.group(1)
        
        try:
            print(f"Getting status of: {url}")
            with urllib.request.urlopen(url) as response:
                status_code = response.getcode()
                content_type = response.headers.get('Content-Type', 'unknown')
                content_length = response.headers.get('Content-Length', 'unknown')
                server = response.headers.get('Server', 'unknown')
                
                print(f"Status Code: {status_code}")
                print(f"Content-Type: {content_type}")
                print(f"Content-Length: {content_length}")
                print(f"Server: {server}")
                
                return f"urllib.request.urlopen('{url}').getcode()"
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            print(f"Status Code: {e.code}")
            return None
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            return None
        except Exception as e:
            print(f"Error getting status: {e}")
            return None
    
    # === BLOCK PATTERN HANDLERS (Python-style indentation support) ===
    
    def _if_block_start(self, match):
        """Handle the start of an if block"""
        condition = match.group(1).strip()
        return f"# if {condition}: (block structure)"
    
    def _else_block_start(self, match):
        """Handle the start of an else block"""
        return "# else: (block structure)"
    
    def _foreach_block_start(self, match):
        """Handle the start of a for each block"""
        loop_spec = match.group(1).strip()
        return f"# for each {loop_spec}: (block structure)"
    
    def _while_block_start(self, match):
        """Handle the start of a while block"""
        condition = match.group(1).strip()
        return f"# while {condition}: (block structure)"
    
    def _repeat_block_start(self, match):
        """Handle the start of a repeat block"""
        count = match.group(1).strip()
        return f"# repeat {count} times: (block structure)"
    
    def _function_block_start(self, match):
        """Handle the start of a function block without parameters"""
        func_name = match.group(1).strip()
        return f"# define function {func_name}: (block structure)"
    
    def _function_with_params_start(self, match):
        """Handle the start of a function block with parameters"""
        func_name = match.group(1).strip()
        params = match.group(2).strip()
        return f"# define function {func_name} with {params}: (block structure)"
    
    # === BLOCK EXECUTION METHODS ===
    
    def execute_block(self, block: BlockContext):
        """Execute a block with proper context and scope"""
        # Save current state for scope management
        if block.block_type == 'function':
            # Functions get their own scope
            old_vars = self.variables.copy()
            
        try:
            # Execute the block based on its type
            if block.block_type == 'conditional':
                self._execute_conditional_block(block)
            elif block.block_type == 'foreach':
                self._execute_foreach_block(block)
            elif block.block_type == 'while':
                self._execute_while_block(block)
            elif block.block_type == 'repeat':
                self._execute_repeat_block(block)
            elif block.block_type == 'function':
                self._execute_function_block(block)
            else:
                # Default: execute all commands in the block
                self._execute_commands_in_block(block)
                
        finally:
            # Restore scope if this was a function
            if block.block_type == 'function':
                self.variables = old_vars
    
    def _execute_conditional_block(self, block: BlockContext):
        """Execute a conditional block (if/else)"""
        # Parse the condition from the header
        header = block.header.strip()
        if header.lower().startswith('if '):
            condition = header[3:].rstrip(':')
            # Convert to single-line format for existing condition logic
            if self._evaluate_condition(condition):
                self._execute_commands_in_block(block)
        elif header.lower() == 'else:':
            # Else blocks are handled by the parent if block
            self._execute_commands_in_block(block)
    
    def _execute_foreach_block(self, block: BlockContext):
        """Execute a for each block"""
        header = block.header.strip()
        # Parse: "for each item in list mylist:"
        if header.lower().startswith('for each '):
            spec = header[9:].rstrip(':')
            # Convert to single-line format for existing logic
            old_break = self.break_loop
            old_continue = self.continue_loop
            self.break_loop = False
            self.continue_loop = False
            
            # Execute the loop using existing logic
            self._execute_foreach_logic(spec, block)
            
            self.break_loop = old_break
            self.continue_loop = old_continue
    
    def _execute_while_block(self, block: BlockContext):
        """Execute a while block"""
        header = block.header.strip()
        if header.lower().startswith('while '):
            condition = header[6:].rstrip(':')
            
            old_break = self.break_loop
            old_continue = self.continue_loop
            
            while self._evaluate_condition(condition) and not self.break_loop:
                self.continue_loop = False
                self._execute_commands_in_block(block)
                
                if self.continue_loop:
                    self.continue_loop = False
                    continue
                    
            self.break_loop = old_break
            self.continue_loop = old_continue
    
    def _execute_repeat_block(self, block: BlockContext):
        """Execute a repeat block"""
        header = block.header.strip()
        if header.lower().startswith('repeat '):
            # Extract the number
            import re
            match = re.search(r'repeat (\d+) times?:', header.lower())
            if match:
                count = int(match.group(1))
                
                old_break = self.break_loop
                old_continue = self.continue_loop
                
                for i in range(count):
                    if self.break_loop:
                        break
                    self.continue_loop = False
                    self._execute_commands_in_block(block)
                    
                    if self.continue_loop:
                        self.continue_loop = False
                        continue
                        
                self.break_loop = old_break
                self.continue_loop = old_continue
    
    def _execute_function_block(self, block: BlockContext):
        """Execute a function definition block"""
        header = block.header.strip()
        
        # Parse function name and parameters
        if 'with ' in header:
            # Function with parameters
            match = re.search(r'define function (\w+) with (.+):', header)
            if match:
                func_name = match.group(1)
                params = [p.strip() for p in match.group(2).split(',')]
                self.block_functions[func_name] = {
                    'block': block,
                    'parameters': params
                }
                print(f"Function '{func_name}' defined with parameters: {', '.join(params)}")
        else:
            # Function without parameters
            match = re.search(r'define function (\w+):', header)
            if match:
                func_name = match.group(1)
                self.block_functions[func_name] = {
                    'block': block,
                    'parameters': []
                }
                # Also add to regular functions for compatibility
                commands = []
                for cmd_info in block.commands:
                    commands.append(cmd_info['command'])
                self.functions[func_name] = '; '.join(commands)
                print(f"Function '{func_name}' defined")
        
        return f"def {func_name}(): # block function"
    
    def _execute_commands_in_block(self, block: BlockContext):
        """Execute all commands in a block"""
        for cmd_info in block.commands:
            command = cmd_info['command']
            line_num = cmd_info['line_number']
            
            print(f"[Line {line_num}] {command}")
            try:
                result = self.process_command(command)
                if result is not None:
                    # Success - command executed
                    pass
                print()  # Empty line for readability
            except Exception as e:
                print(f"ERROR at line {line_num}: {e}")
                print(f"Command: {command}")
                print()
        
        # Execute child blocks in order
        for child_block in block.child_blocks:
            self.execute_block(child_block)
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition using existing conditional logic"""
        # Parse common condition patterns
        import re
        
        # Check for "variable is greater than number"
        match = re.search(r'(\w+) is greater than (\d+)', condition)
        if match:
            var_name = match.group(1)
            threshold = int(match.group(2))
            if var_name in self.variables:
                try:
                    return float(self.variables[var_name]) > threshold
                except:
                    return False
            return False
        
        # Check for "variable is less than number"
        match = re.search(r'(\w+) is less than (\d+)', condition)
        if match:
            var_name = match.group(1)
            threshold = int(match.group(2))
            if var_name in self.variables:
                try:
                    return float(self.variables[var_name]) < threshold
                except:
                    return False
            return False
        
        # Check for "variable equals value"
        match = re.search(r'(\w+) equals? [\'"](.+?)[\'"]', condition)
        if match:
            var_name = match.group(1)
            value = match.group(2)
            if var_name in self.variables:
                return str(self.variables[var_name]) == value
            return False
        
        # Check for "variable equals number"
        match = re.search(r'(\w+) equals? (\d+)', condition)
        if match:
            var_name = match.group(1)
            value = int(match.group(2))
            if var_name in self.variables:
                try:
                    return float(self.variables[var_name]) == value
                except:
                    return False
            return False
        
        # Default: return True for now (should be improved)
        return True
    
    def _execute_foreach_logic(self, spec: str, block: BlockContext):
        """Execute foreach loop logic"""
        # Parse the foreach specification: "item in list listname"
        import re
        match = re.search(r'(\w+) in list (\w+)', spec)
        if match:
            item_var = match.group(1)
            list_name = match.group(2)
            
            if list_name in self.lists:
                for item_value in self.lists[list_name]:
                    if self.break_loop:
                        break
                    if self.continue_loop:
                        self.continue_loop = False
                        continue
                    
                    # Set the loop variable
                    self.variables[item_var] = item_value
                    
                    # Execute commands in the block
                    for cmd_info in block.commands:
                        command = cmd_info['command']
                        line_num = cmd_info['line_number']
                        
                        if self.break_loop:
                            break
                        if self.continue_loop:
                            self.continue_loop = False
                            break
                            
                        print(f"[Line {line_num}] {command}")
                        try:
                            result = self.process_command(command)
                            print()
                        except Exception as e:
                            print(f"ERROR at line {line_num}: {e}")
                            print()
            else:
                print(f"Error: List '{list_name}' not found!")
        else:
            print(f"Error: Invalid foreach specification: {spec}")
    
    def process_command(self, command):
        """Process a natural language command with support for nested function calls"""
        command = command.strip()
        
        if not command:
            return None
        
        # Prevent excessively long commands that could cause issues
        if len(command) > 1000:
            print("Error: Command too long (max 1000 characters)")
            return None
        
        try:
            # Check for nested function calls and expand them
            command = self._expand_function_calls(command)
            
            # First try block patterns (higher priority)
            for compiled_pattern, handler in self.compiled_block_patterns:
                match = compiled_pattern.search(command)
                if match:
                    generated_code = handler(match)
                    if generated_code:
                        print(f"[Generated: {generated_code}]")
                    return generated_code
            
            # Then try single-line patterns (backward compatibility)
            for compiled_pattern, handler in self.compiled_patterns:
                match = compiled_pattern.search(command)
                if match:
                    generated_code = handler(match)
                    if generated_code:
                        print(f"[Generated: {generated_code}]")
                    return generated_code
            
            # No pattern matched
            print(f"Sorry, I don't understand: '{command}'")
            suggestions = self._get_command_suggestions(command)
            if suggestions:
                print("Did you mean:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
            else:
                print("Type 'help' to see available commands.")
            return None
            
        except Exception as e:
            print(f"Error processing command: {e}")
            return None
    
    def _get_command_suggestions(self, command):
        """Generate helpful suggestions for unrecognized commands"""
        suggestions = []
        command_lower = command.lower()
        
        # Common command corrections
        common_fixes = {
            'print': ['print "text"', 'print variable_name'],
            'create': ['create variable name as value', 'create list name with item1, item2'],
            'set': ['set variable_name to value'],
            'add': ['add 5 and 3', 'add "item" to list list_name'],
            'if': ['if variable equals value then action'],
            'repeat': ['repeat 5 times: action'],
            'for': ['for each item in list name do action'],
            'define': ['define function name as action'],
            'call': ['call function name'],
            'save': ['save to file "filename.txt"', 'save session to "session.json"'],
            'load': ['load from file "filename.txt"', 'load session from "session.json"'],
            'show': ['show list name', 'show variables'],
            'calculate': ['calculate 5 + 3', 'calculate sine of 45'],
            'convert': ['convert variable to string', 'convert variable to number'],
            'check': ['check if file "name.txt" exists', 'check type of variable'],
        }
        
        # Check for partial matches with common commands
        for cmd, examples in common_fixes.items():
            if cmd in command_lower:
                suggestions.extend(examples[:2])  # Add up to 2 examples
        
        # Check for common typos and variations
        typo_fixes = {
            'prin': 'print',
            'pront': 'print', 
            'priny': 'print',
            'crete': 'create',
            'creat': 'create',
            'ad': 'add',
            'repet': 'repeat',
            'cal': 'call',
            'sav': 'save',
            'lod': 'load',
            'shw': 'show',
            'def': 'define',
        }
        
        for typo, correction in typo_fixes.items():
            if typo in command_lower and correction in common_fixes:
                suggestions.extend([f"{correction} (corrected from '{typo}')"]) 
                suggestions.extend(common_fixes[correction][:1])
        
        # Context-aware suggestions based on current state
        if 'variable' in command_lower and self.variables:
            suggestions.append(f"Available variables: {', '.join(list(self.variables.keys())[:3])}")
        
        if 'list' in command_lower and self.lists:
            suggestions.append(f"Available lists: {', '.join(list(self.lists.keys())[:3])}")
        
        if 'function' in command_lower and self.functions:
            suggestions.append(f"Available functions: {', '.join(list(self.functions.keys())[:3])}")
        
        # Math-related suggestions
        if any(word in command_lower for word in ['math', 'calculate', 'compute', '+', '-', '*', '/', 'number']):
            suggestions.extend([
                'add 5 and 3',
                'calculate 10 * 2', 
                'calculate sine of 45'
            ])
        
        # File operation suggestions
        if any(word in command_lower for word in ['file', 'save', 'load', 'read', 'write']):
            suggestions.extend([
                'save to file "data.txt"',
                'load from file "data.txt"',
                'check if file "name.txt" exists'
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:3]  # Return top 3 suggestions to prevent excessive output
    
    def _expand_function_calls(self, command):
        """Expand function calls within commands"""
        # Look for patterns like "call function_name" within the command
        import re
        function_call_pattern = r'call (\w+)'
        
        def replace_function(match):
            func_name = match.group(1)
            if func_name in self.functions:
                return self.functions[func_name]
            return match.group(0)  # Return original if function not found
        
        # Replace function calls with their definitions
        expanded = re.sub(function_call_pattern, replace_function, command)
        return expanded
    
    def execute_script(self, filename):
        """Execute a vernacular script file (.vern) with support for both single-line and block structure"""
        try:
            if not os.path.exists(filename):
                print(f"Error: Script file '{filename}' not found!")
                return False
            
            print(f"=== Executing Vernacular Script: {filename} ===")
            print()
            
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Check if this script uses block structure (contains lines ending with ':')
            has_block_structure = any(line.strip().endswith(':') and 
                                    self.block_parser.is_block_start(line.strip()) 
                                    for line in lines)
            
            if has_block_structure:
                return self._execute_block_script(filename, lines)
            else:
                return self._execute_single_line_script(filename, lines)
                
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found!")
            return False
        except PermissionError:
            print(f"Error: Permission denied reading '{filename}'!")
            return False
        except UnicodeDecodeError:
            print(f"Error: Unable to decode '{filename}' - not a valid text file!")
            return False
        except Exception as e:
            print(f"Error executing script: {e}")
            return False
    
    def _execute_single_line_script(self, filename, lines):
        """Execute a script with single-line commands (original behavior)"""
        total_lines = len(lines)
        executed_lines = 0
        successful_lines = 0
        
        for line_num, line in enumerate(lines, 1):
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            executed_lines += 1
            print(f"[Line {line_num}] {line}")
            
            try:
                result = self.process_command(line)
                if result is not None:
                    successful_lines += 1
                print()  # Empty line for readability
            except Exception as e:
                print(f"ERROR at line {line_num}: {e}")
                print(f"Command: {line}")
                print()
                return False
        
        print("=== Script Execution Complete ===")
        print(f"Total lines in file: {total_lines}")
        print(f"Lines executed: {executed_lines}")
        print(f"Successful commands: {successful_lines}")
        print(f"Success rate: {(successful_lines/executed_lines)*100:.1f}%" if executed_lines > 0 else "Success rate: N/A")
        
        return True
    
    def _execute_block_script(self, filename, lines):
        """Execute a script with block structure (new Python-style indentation)"""
        print("Block structure detected - using enhanced parser...")
        print()
        
        # Parse the script into block structure
        parser = BlockParser()
        blocks = parser.parse_lines(lines)
        
        print(f"Parsed {len(blocks)} top-level items")
        
        total_lines = len(lines)
        executed_commands = 0
        successful_commands = 0
        
        # Execute each top-level block or command
        for item in blocks:
            if isinstance(item, BlockContext):
                # This is a block structure
                print(f"Executing block: {item.header} (line {item.line_number})")
                try:
                    self.execute_block(item)
                    executed_commands += 1
                    successful_commands += 1
                except Exception as e:
                    print(f"ERROR executing block starting at line {item.line_number}: {e}")
                    print(f"Block header: {item.header}")
                    print()
                    return False
            elif isinstance(item, dict) and 'command' in item:
                # This is a single command
                command = item['command']
                line_num = item['line_number']
                
                executed_commands += 1
                print(f"[Line {line_num}] {command}")
                
                try:
                    result = self.process_command(command)
                    if result is not None:
                        successful_commands += 1
                    print()  # Empty line for readability
                except Exception as e:
                    print(f"ERROR at line {line_num}: {e}")
                    print(f"Command: {command}")
                    print()
                    return False
        
        print("=== Script Execution Complete ===")
        print(f"Total lines in file: {total_lines}")
        print(f"Commands/blocks executed: {executed_commands}")
        print(f"Successful operations: {successful_commands}")
        print(f"Success rate: {(successful_commands/executed_commands)*100:.1f}%" if executed_commands > 0 else "Success rate: N/A")
        
        return True
    
    def benchmark_performance(self, test_commands=None, iterations=1000):
        """Benchmark pattern matching performance"""
        import time
        
        if test_commands is None:
            test_commands = [
                'print "hello world"',
                'add 5 and 3', 
                'set variable to 10',
                'repeat 3 times: print "test"',
                'if x equals 5 then print "match"',
                'create list items with 1, 2, 3',
                'call function test',
                'calculate sine of 45',
                'save to file "test.txt"',
                'check type of variable'
            ]
        
        print(f"Benchmarking {iterations} iterations with {len(test_commands)} commands...")
        
        # Test compiled patterns (current implementation)
        start_time = time.time()
        for _ in range(iterations):
            for command in test_commands:
                for compiled_pattern, handler in self.compiled_patterns:
                    match = compiled_pattern.search(command)
                    if match:
                        break
        compiled_time = time.time() - start_time
        
        # Test old method (re.search with flags each time)
        start_time = time.time()
        for _ in range(iterations):
            for command in test_commands:
                for pattern, handler in self.patterns:
                    match = re.search(pattern, command, re.IGNORECASE)
                    if match:
                        break
        old_time = time.time() - start_time
        
        improvement = ((old_time - compiled_time) / old_time) * 100
        
        print(f"Performance Results:")
        print(f"  Old method (re.search): {old_time:.4f}s")
        print(f"  Compiled patterns: {compiled_time:.4f}s")
        print(f"  Performance improvement: {improvement:.1f}%")
        print(f"  Speedup factor: {old_time / compiled_time:.2f}x")
        
        return {
            'old_time': old_time,
            'compiled_time': compiled_time,
            'improvement_percent': improvement,
            'speedup_factor': old_time / compiled_time
        }

def run_repl():
    """Run the interactive REPL mode"""
    nlp = NaturalLanguageProcessor()
    
    # Check if input is piped or redirected
    if not sys.stdin.isatty():
        # Process piped input
        try:
            for line in sys.stdin:
                command = line.strip()
                if command and not command.startswith('#'):
                    # Handle quit commands in piped input
                    if command.lower() in ['quit', 'exit', 'bye']:
                        print("Goodbye!")
                        break
                    nlp.process_command(command)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")
        return
    
    print("=== Natural Language Programming REPL ===")
    print("Type commands in plain English. Type 'quit' to exit, 'help' for commands.")
    print()
    
    while True:
        try:
            command = input(">>> ").strip()
            
            if command.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if command:
                nlp.process_command(command)
                print()  # Empty line for readability
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description='Vernacular - Natural Language Programming System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python vernacular.py                    # Start interactive REPL
  python vernacular.py script.vern        # Execute a .vern script file
  python vernacular.py examples/hello_world.vern -v    # Execute example with verbose output
  python vernacular.py --version          # Show version information

Script files (.vern) support:
  - Comments with # or //
  - All vernacular commands
  - Error reporting with line numbers
        '''
    )
    
    parser.add_argument('script', nargs='?', help='Vernacular script file to execute (.vern)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--version', action='version', version='Vernacular 3.0 - Python-Style Block Structure Programming')
    
    args = parser.parse_args()
    
    # Create processor instance
    nlp = NaturalLanguageProcessor()
    
    if args.script:
        # Script execution mode
        if not args.script.endswith('.vern'):
            print("Warning: Script file should have .vern extension")
        
        if args.verbose:
            print(f"Executing script: {args.script}")
            print(f"Verbose mode: ON")
            print()
        
        success = nlp.execute_script(args.script)
        sys.exit(0 if success else 1)
    else:
        # Interactive REPL mode
        run_repl()

if __name__ == "__main__":
    main()

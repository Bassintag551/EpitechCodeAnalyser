#!/usr/bin/python
# CODE ANALYSER written by Antoine Stempfer #
# This script is used to help students of Epitech to check their c files #

import sys
import os
import re

class colors:
    clear = '\033[0;74m'
    error = '\033[1;31m'
    good = '\033[0;32m'
    warning = '\033[1;33m'
    bold = '\033[1m'

def log(message, color=colors.clear):
    print(color + message + colors.clear);

def log_error(error_type, location="in file", advice=None, line=None):
    log("\n/!\\ AN ERROR HAS BEEN FOUND /!\\", colors.error)
    log("Error Details:")
    log("   Error type: %s" % error_type)
    log("   Error location: %s" % location)
    if line is not None:
        log("   |-> Line: %s " % line)
    if advice is not None:
        log("   Advice: " + advice)
    log("--------------------------------\n")
    global error_count
    error_count += 1    

def open_source_file(path):
    if not os.path.isfile(path):
        print("Fatal: the provided file does not exist")
        return None
    if not path.endswith(".c"):
        log_error("Illegal file extension", "File name", "Rename file to <file name>.c")
        return None
    f = open(path)
    return f

def scan_file(f):
    lines = [l.replace("\t", "        ") for l in f]
    check_header(lines)
    line_number = 9
    function_count = 0
    identation = 0
    while line_number < len(lines):
        line = lines[line_number]
        if len(line) > 80:
            log_error("Illegal line length (> 80)", "line %i" % (line_number + 1), "Rename your variables with shorter names or refactor your expression", line)
        if line.endswith(" \n"):
            log_error("White space at the end of a line", "line %i" % (line_number + 1), "Remove the whitespace", line)
        if re.match("^(\w+(\s+)?){2,}\(([^!@#$+%^]+)?\)", line):
            function_count += 1 
            if "{" in line:
                log_error("Illegal bracket position", "line %i" % (line_number + 1), "Place the bracket on the next line", line)
            else:
                check_method(lines, line_number + 1)
            if function_count > 5:
                log_error("Illegal number of functions (> 5)", "line %i (whole function)" % (line_number + 1), "Remove or merge some functions", line)
        if re.match("^(\s+)?{", lines[line_number - 1]):
            identation += 2
        if re.match("^(\s+)?((else if|if|while|for)(\s+|\()|else(\s+)?)", lines[line_number - 1]):
            identation += 2
        if re.match("^.*}(\s+)?$", line):
            identation -= 2
        if re.match("^(\s+)?((else if|if|while|for)(\s+|\()|else(\s+)?)", lines[line_number - 2]) and not "{" in lines[line_number - 2] and not "{" in lines[line_number - 1]:
            identation -= 2
        if re.match("^.*}(\s+)?$", lines[line_number - 1]):
            identation -= 2
        if line.strip() != "":
            spaces = len(line) - len(line.lstrip())
            if not spaces == identation:
                log_error("Illegal identation (expected %i spaces)" % identation, "line %i" % (line_number + 1), "Fix your identation with C-c C-q or use Tab", line)
                identation = spaces
        line_number += 1
        
def check_method(lines, starting_line):
    if not lines[starting_line].endswith("{\n"):
        log_error("Illegal function syntax", "line %i" % starting_line, "This line should only contain the opening bracket", lines[starting_line])
    brackets_to_close = 1
    initializing_vars = True
    line_index = starting_line
    lines_count = 0
    while not brackets_to_close == 0:
        line_index += 1
        lines_count += 1
        line = lines[line_index]
        if "{" in line:
            if line.strip() is not "{":
                log_error("Illegal bracket postition", "line %i" % (line_index + 1), "Brackets should be on their own lines", line)
            brackets_to_close += 1
        elif "}" in line:
            if line.strip() is not "}":
                log_error("Illegal bracket postition", "line %i" % (line_index + 1), "Brackets should be on their own lines", line)
            brackets_to_close -= 1
        if re.match("^(\s+\w+)?(\s+)?\w+\*?\s+\*?\w+(\s+)?=(\s+)?", line):
            if initializing_vars:
                log_error("Illegal variable initialization", "line %i" % (line_index + 1), "Initialize this variable in a separate line from it's declaration", line)
            else:
                log_error("Illegal variable declaration", "line %i" % (line_index + 1), "Declare this variable before executing commands in this function", line)
        if initializing_vars:
            if line.strip() == "":
                initializing_vars = False
            elif not re.match("^(\s+\w+)?(\s+)?\w+\*?\s+\*?\w+(\[.*\])?;", line):
                initializing_vars = False
                if not lines_count == 1:
                    log_error("Missing empty line", "line %i" % (line_index + 1), "Add an empty line after you're done declaring your variables", line)
        else:
            if re.match("^(\s+\w+)?(\s+)?\w+\*?\s+\*?\w+(\[.*\])?;", line) and not re.match("^\s+?return", line) and not "=" in line:
                log_error("Illegal variable declaration", "line %i" % (line_index + 1), "Declare this variable before executing commands in this method", line)
            elif line.strip() == "":
                log_error("Illegal empty line", "line %i" % (line_index + 1), "Remove this empty line", line)
            elif re.match("^\s+return(\s+?|;|\()", line):
                if re.match("^(\s+)?return\(", line):
                    log_error("Missing whitespace", "line %i" % (line_index + 1), "Add an empty space in between \"return\" and \"(\"", line)
                if re.match("^(\s+)?return\s+\w", line):
                    log_error("Missing surrounding parenthesis", "line %i" % (line_index + 1), "Add parenthesis before and after your value", line)
            elif re.match("^(\s+)?(else if|if|while)\(", line):
                log_error("Missing whitespace", "line %i" % (line_index + 1), "Add a white space between your flow control keyword and it's following parenthesis", line)
            elif re.match("^(\s+)?(for|switch)(\s+)?\(", line):
                log_error("Illegal C keyword", "line %i" % (line_index + 1), "Remove the incorrect keywords (for, switch, ...)", line);
    if lines_count - 1 > 25:
        log_error("Illegal number of lines in function (%i > 25)" % (lines_count - 1), "line %i" % (line_index - lines_count % 25), "Reduce number of lines, try using less variables for example")
    return line_index - starting_line
        
def check_header(lines):
    def log_header_error(line=1):
        log_error("Missing or invalid header", "line %s" % (line + 1), "Remove existing header and use C-c C-h in emacs to generate a new one", lines[line])
    if len(lines) < 9:
        log_header_error()
    header_lines = lines[:9]
    if not header_lines[0].startswith("/*"):
        log_header_error(0)
    for l in range(0, 7):
        line = header_lines[l+1]
        if not line.startswith("**"):
            log_header_error(l + 1)
    if not header_lines[8].startswith("*/"):
        log_header_error(8)

def main():
    args = sys.argv
    if len(args) is 1:
        log("Fatal: You must specify a file to analyse")
        return
    global error_count
    error_count = 0
    log("\n/!\\ DISCLAIMER /!\\", colors.warning)
    log("Compile your files before using this utility")
    log("This utility isn't official and is only here to help you make less mistakes, DO NOT use it as a way to ensure your code is correct")
    log("USING THIS ON PROJECT SOURCE FILES IS CONSIDERED CHEATING, USE AT YOUR OWN RISK,I AM IN NO WAY RESPONSIBLE FOR YOUR USAGE OF THIS SCRIPT\n", colors.bold)
    f = open_source_file(args[1])
    if not f:
        return
    scan_file(f)
    log("Done checking %s" % args[1])
    if error_count > 0:
        log("There is a grand total of %i error(s) in your file" % error_count)
    else:
        log("No error has been detected, however this script might not find everything so be carefull", colors.good)
    
if __name__ == "__main__":
    main()

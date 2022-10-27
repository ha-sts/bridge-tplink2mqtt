#!/usr/bin/env python3

import os
import sys

from radon.complexity import cc_rank, cc_visit
from radon.visitors import Function, Class

# Add directories to exclude to this list.
EXCLUDE_DIRS = ['venv']

def get_python_modules():
    # Get a list of all python files in the project
    print('Compiling list of modules...')
    modules = []
    for i in os.walk(os.path.abspath(os.path.join(os.path.abspath(__file__), '..')), topdown = True):
        root, dirs, files = i
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith('.py'):
                modules.append(os.path.join(root, file))
    return modules

def add_to_report(scores, chunk, template):
    lines = "{}-{}".format(chunk.lineno, chunk.endline)
    scores.append(chunk.complexity)
    complexity = cc_rank(chunk.complexity)
    if isinstance(chunk, Function):
        if chunk.is_method is False:
            print(template.format(lines, 'Function', complexity, chunk.name))
        else:
            print(template.format(lines, 'Method', complexity, '{}.{}'.format(chunk.classname, chunk.name)))
    elif isinstance(chunk, Class):
        print(template.format(lines, 'Class', complexity, chunk.name))
        for method in chunk.methods:
            add_to_report(scores, method, template)

def main():
    # Analyze each module with Radon
    print('Analyzing modules with Radon...')
    results = {}
    for mod in get_python_modules():
        with open(mod, 'r', encoding = 'utf-8') as py_file:
            results[mod] = cc_visit(py_file.read())

    # Generate a report and save it to a file
    print('Generating report...')
    template = "  {0:8} {1:9} {2:6} {3:20}"
    scores = []

    for key,value in results.items():
        if not value:
            continue
        print(key + '\n' + template.format('Lines', 'Type', 'Score', 'Name'))
        for chonk in value:
            if isinstance(chonk, Function) and chonk.is_method:
                continue
            add_to_report(scores, chonk,template)

    # Create a summary of the analysis
    print('\nFiles analyzed: {}\nAverage score: {}\n\n'.format(str(len(scores)), str(sum(scores)/len(scores))))

    # If the complexity of a module is above 10 (a 'c' grade), return a non-zero exit code
    if max(scores) > 10:
        print('Analysis score too low, exiting with error code 1')
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

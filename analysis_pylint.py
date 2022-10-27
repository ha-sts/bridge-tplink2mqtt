#!/usr/bin/env python3

import io
import os
import sys

from pylint.lint import Run
from pylint.reporters.text import TextReporter

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

def run_pylint(module):
    print(module)
    tmp_output = io.StringIO()
    tmp_reporter = TextReporter(tmp_output)
    Run([module], reporter = tmp_reporter, exit = False)
    return tmp_output.getvalue()

def get_result_value(result_string):
    tmp_res_list = result_string.rstrip().split('\n')
    for item in tmp_res_list:
        if 'Your code has been rated at' in item:
            tmp_result = float(item.split()[6].split('/')[0])
            return tmp_result
    return None

def main():
    # Run PyLint on all of the modules, keeping the output
    results = {}
    print("\nAnalyzing modules with PyLint...")
    for mod in get_python_modules():
        results[mod] = run_pylint(mod)

    # Generate a report to save in the project, keeping track of scores
    print('\nGenerating report...')
    report = '--- Report ---\n'
    scores = []
    for key,value in results.items():
        report += '{}\n'.format(key)
        report += value.replace(' {}:'.format(key), 'line ')
        report += '\n\n'

        # Get the score of the result
        tmp_score = get_result_value(value)
        if tmp_score:
            scores.append(tmp_score)

    # Create a summary of the analysis
    analysis = 'Files analyzed: {}\nAverage score: {}\n\n'.format(str(len(scores)), str(sum(scores)/len(scores)))
    report = report + analysis

    # Dump report to console
    print('\n')
    print(report)

    # Exit with a non-zero code if a score was too low
    if min(scores) < 6:
        print('Analysis score too low, exiting with error code 1')
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

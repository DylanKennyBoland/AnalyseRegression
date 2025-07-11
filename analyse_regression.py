#!/usr/bin/env python3
#
# Author: Dylan Boland
#
# ==== A Script to Analyse the Results of a Regression ====
# It returns:
#
# A list of all the error signatures (marks or IDs) which occurred
# in the regression and their counts (i.e., their frequency).

# Let's import the modules which we will need:
import argparse
from argparse import RawTextHelpFormatter
import re
import os
import sys

# ==== Some General-info Strings ====
# Tags - define these here so they can be quickly and easily changed
errorTag   = """\t***Error: """
successTag = """\t***Success: """
infoTag    = """\t***Info: """

# String to indicate the name of the repository:
repoName = "mcip"

# Standard help & error messages
optionalArgsMsg = """
--config <name_of_config>: The script will only analyse the regression results corresponding
to the configuration specified on the command line.
--fast_search: A boolean switch (or option) which instructs the script to search the short
(compressed) status file rather than the full log file. The short status file is typically
80-100 lines long, whereas the log file can be 100s of thousands of lines. As such, using
this option speeds up the execution of the script.

However, searching the full log files will result in more accurate numbers (data).
"""
helpMsg = infoTag + f"""This script should be called in the {repoName} directory
or in one of its subdirectories (e.g., the 'build' directory).

The following optional arguments may be supplied:
""" + optionalArgsMsg
invalidArgsMsg  = errorTag + """This script only supports the following optional arguments:
""" + optionalArgsMsg
descriptionMsg = """A Script to Analyse the Results of a Regression.
It returns:

A list of all the error signatures (marks or IDs) which occurred
in the regression and their counts (i.e., their frequency)."""
noArgsMsg = infoTag + "No optional arguments were supplied."

noSuchFileMsg   = errorTag + """The module file '{}' could not be located - double-check the name or file path."""
fileReadSuccess = successTag + """The module file was read in successfully."""
fileReadError   = errorTag + """The module file could not be read in successfully."""
moduleNameNotIdentified = errorTag + """The module name could not be identified. Please ensure that you have used
\ta standard or conventional structure. An example is shown below:
            module serialTX #
                (
                parameter INCR = 26'd25770 // amount by which the accumulator is incremented
                )
                (
                input clk,
                input reset,
                input [7:0] data,
                input send,
                output reg txOut,
                output busy
                );
                // The module description or logic goes below
"""
noParamsFound       = infoTag + """No parameters were identified for this module."""
noInputsIdentified  = errorTag + """No module inputs were identified."""
noOutputsIdentified = errorTag + """No module outputs were identified."""
configSuppliedMsg = infoTag + """The following configuration has been supplied on the command line: {}"""
fastSearchRequestedMsg = infoTag + """A fast search has been requested on the command line."""

# Instantiated module print-out message
jobDoneMsg = """
\n\n\t===========================================================================
\t\tAdditionally, you can see the regression analysis below!
\t==========================================================================="""

# Goodbye message
goodbyeMsg = """
\t===========================================================================================
\t\tSuccess! The analysis report is at {}.
\t==========================================================================================="""

# Some Header (Delimiter) Strings
# These allow us to cleary separate input and
# output ports when instantiating the module
inputPortsHeader = """// ==== Inputs ===="""
outputPortsHeader = """// ==== Outputs ====\n\t"""
paramsHeader = """// ==== Parameters ===="""

# Function to handle the input arguments
def parsingArguments():
    parser = argparse.ArgumentParser(description = descriptionMsg, formatter_class = RawTextHelpFormatter)
    parser.add_argument('--config', type = str, required = False, help = helpMsg)
    parser.add_argument('--fast_search', action = 'store_true', required = False, help = helpMsg)
    return parser.parse_args()

if __name__ == "__main__":
    args = parsingArguments() # parse the input arguments (if there are any)
    argsSupplied = True
    configSupplied = False
    fastSearchRequested = False
    if len(sys.argv) == 1:
        print(noArgsMsg)
        argsSupplied = False
    elif args.config is not None:
        configName = args.config
        configSupplied = True
        print(configSuppliedMsg.format(configName))
        if args.fast_search:
            fastSearchRequested = True
            print(fastSearchRequestedMsg)
    elif args.fast_search:
        fastSearchRequested = True
        print(fastSearchRequestedMsg)
    # ==== Step 1: Get the Path to the Current Work Directory (CWD) ====
    cwd = os.getcwd()
    # ==== Step 2: Get the Name of the Folder in which the Repository is Cloned ====
    cwdSplitUp = cwd.split("\\") # Split the path to the current working directory up
    # Check if some segment of the path *is* the name of the repository:
    pathContainsRepo = repoName in cwdSplitUp
    indexOfReposFolder = 0
    if (pathContainsRepo):
        cwdSplitUpReversed = list(reversed(cwdSplitUp))
        indexOfReposFolder = cwdSplitUpReversed.index(repoName)
        if indexOfReposFolder != (len(cwdSplitUpReversed) - 1):
            indexOfReposFolder = indexOfReposFolder + 1
    scratchFolderName = cwdSplitUpReversed[indexOfReposFolder]
    userName = os.environ.get('USERNAME')
    scratchDirBaseName = f"/lan/{userName}/{scratchFolderName}/"
    print(cwdSplitUp)
    print(scratchFolderName)
    print(scratchDirBaseName)
    exit()

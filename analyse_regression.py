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
errorTag   = """***Error: """
successTag = """***Success: """
infoTag    = """***Info: """

# String to indicate the name of the repository:
repoName = "mcip"

# String to indicate the base directory of the scratch folder:
pathToScratchArea = "/lan/dscratch/"

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
fileReadSuccess = successTag + """The log file at {} was read in successfully."""
configSuppliedMsg = infoTag + """The following configuration has been supplied on the command line: {}"""
fastSearchRequestedMsg = infoTag + """A fast search has been requested on the command line."""
verbosityEnabledMsg = infoTag + """Verbosity has been enabled from the command line."""

# Error messages:
noSuchConfigMsg = errorTag + """The config '{}' could not be located - double-check the name."""
fileReadError   = errorTag + """The log file at {} file could not be read in successfully."""
wrongDirectoryMsg = errorTag + f"""The script appears to have been called from the wrong directory.
The {repoName} repository can't be found."""

# End print-out message
scriptOpeningMsg = """
\n\n\t================================================================================
\t\t Running {} to Analyse the Regression Results
\t================================================================================
"""

# End print-out message
jobDoneMsg = """
\n\n\t===========================================================================
\t\tAdditionally, you can see the regression analysis below!
\t==========================================================================="""

# Goodbye message
goodbyeMsg = """
\t===========================================================================================
\t\tSuccess! The analysis report is at {}.
\t==========================================================================================="""

# Function to handle the input arguments
def parsingArguments():
    parser = argparse.ArgumentParser(description = descriptionMsg, formatter_class = RawTextHelpFormatter)
    parser.add_argument('--config', type = str, required = False, help = helpMsg)
    parser.add_argument('--fast_search', action = 'store_true', required = False, help = helpMsg)
    parser.add_argument('--verbose', '-v', action = 'store_true', required = False, help = helpMsg)
    return parser.parse_args()

if __name__ == "__main__":
    # ==== Preliminary Step: Print an Opening (Start) Message ====
    scriptName = "analyse_regression.py"
    print(scriptOpeningMsg.format(scriptName))

    # ==== Step 1: Get the Path to the Current Work Directory (CWD) ====
    cwd = os.getcwd()

    # ==== Step 2: Get the Name of the Folder in which the Repository is Cloned ====
    cwdSplitUp = cwd.split("\\") # Split the path to the current working directory up

    # Check if some segment of the path *is* the name of the repository:
    pathContainsRepo = repoName in cwdSplitUp
    # If the repo name is not found, alert the user and exit:
    if not pathContainsRepo:
        print(wrongDirectoryMsg)
        exit()

    # ==== Step 3: Parse the Input Arguments (if there are any) ====
    args = parsingArguments() # parse the input arguments (if there are any)
    if len(sys.argv) == 1:
        print(noArgsMsg)

    verbosityEnabled = False
    if args.verbose:
        verbosityEnabled = True
        print(verbosityEnabledMsg)

    configSupplied = False
    if args.config is not None:
        configName = args.config
        configSupplied = True
        print(configSuppliedMsg.format(configName))

    fastSearchRequested = False
    if args.fast_search:
        fastSearchRequested = True
        print(fastSearchRequestedMsg)

    # ==== Step 4: Get the User's Name ====
    userName = os.environ.get('USERNAME')

    # ==== Step 5: Extract the Segment of the Path between /home/<user>/ and the Repo itself ====
    # Reverse the split up path (PWD or CWD) and find the first
    # instance of the repository name. This will correspond to the last
    # instance of the repository name in the original, non-reversed list.
    cwdSplitUpAndReversed = list(reversed(cwdSplitUp))
    positionOfRepoInPath = len(cwdSplitUp) - cwdSplitUpAndReversed.index(repoName) - 1
    positionOfUserNameInPath = cwdSplitUp.index(userName)
    pathFromScratchBaseArea = cwdSplitUp[positionOfUserNameInPath:positionOfRepoInPath]
    exit()
    # ==== Step 6: Change Directory to the Scratch Folder with the Results ====

    if (pathContainsRepo):
        cwdSplitUpReversed = list(reversed(cwdSplitUp))
        indexOfReposFolder = cwdSplitUpReversed.index(repoName)
        if indexOfReposFolder != (len(cwdSplitUpReversed) - 1):
            indexOfReposFolder = indexOfReposFolder + 1
    reposFolderName = cwdSplitUpReversed[indexOfReposFolder]
    userName = os.environ.get('USERNAME')
    scratchDirBaseName = f"/lan/{userName}/{reposFolderName}/"

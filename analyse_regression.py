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
pathToScratchBaseArea = "/lan/dscratch"

# String indicating the start pattern which is common to all the configurations:
configNameStartPattern = "cadence."

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
pathDoesNotExistMsg = errorTag + """The directory below does not exist:
{}
"""
configFoundMsg = infoTag + """The {} config has been located!"""
numConfigsFoundMsg = infoTag + """{} configs were found in the results area. They are:
"""
analysingConfigMsg = infoTag + """Analysing the results for {}."""
noResultsForConfigMsg = infoTag + """There are no 'run_<seed_number>' directories for {}."""
runDirsForConfigMsg = infoTag + """There are {} 'run_<seed_number>' directories for {}."""
analysingRunDirMsg = infoTag + """Analysing {}."""

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

    # ==== Step 2: Check that the Repo is Somewhere on the Path ====
    # Split up the path to the current working directory by removing
    # the "\" characters. The various folder names will be put into
    # a list:
    cwdSplitUp = cwd.split("\\")

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
    foldersBetweenHomeDirectoryAndRepo = cwdSplitUp[positionOfUserNameInPath:positionOfRepoInPath]
    # Reinsert the path delimiters (\) in order to form a valid path:
    pathBetweenHomeDirectoryAndRepo = "/"
    for folder in foldersBetweenHomeDirectoryAndRepo:
        pathBetweenHomeDirectoryAndRepo += folder + "/"

    # ==== Step 6: Form the Path to the Scratch Folder with the Results ====
    pathToConfigs = f"{repoName}/mem/"
    pathToScratchArea = pathToScratchBaseArea + pathBetweenHomeDirectoryAndRepo + pathToConfigs
    # Also, check if the path exists. If it doesn't, alert the
    # user and exit:
    pathToScratchArea = "./mem" # temporarily doing this so that I can continue testing as I write the script
    if not os.path.isdir(pathToScratchArea):
        print(pathDoesNotExistMsg.format(pathToScratchArea))
        exit()

    # ==== Step 6: Change Directory to the Scratch Folder with the Results ====
    os.chdir(pathToScratchArea)

    # ==== Step 7: If the User has Specified a Config, Check that it Exists ====
    if configSupplied:
        if not os.path.isdir(configName):
            print(noSuchConfigMsg.format(configName))
            exit()
        elif verbosityEnabled:
            print(configFoundMsg.format(configName))

    # ==== Step 8: Gather all of the Config Names into a List ====
    configNames = [] # an empty list at the moment
    if configSupplied:
        configNames.append(configName)
    else:
        configNames = [folderName for folderName in os.listdir() if folderName.startswith(configNameStartPattern)]

    numConfigsFound = len(configNames)
    # If the user hasn't specified a configuration on the command
    # line and they have enabled verbosity, then inform them of
    # how many configurations were found and list them:
    if verbosityEnabled and not configSupplied:
        print(numConfigsFoundMsg.format(numConfigsFound))
        for name in configNames:
            print(name)

    # ==== Step 9: Define the Regular Expressions which We Need ====
    # TODO: This is the tricky part!

    # ==== Step 10: Get the Results for Each Configuration ====
    # In each test result directory, there will be a log file for us
    # to check. Let's define the format of the file name below:
    logFileNamePattern = "seed{}_ius.log.LSFlog.gz"
    # Also, if the user has requested for a "fast check" or
    # "fast analysis", then we will search the "status" file instead
    # of the log file:
    if fastSearchRequested:
        logFileNamePattern = "status_is."

    # All the test result directories will start with:
    # "run_". Define this as the start pattern for
    # a result directory:
    runFolderStartPattern = "run_"

    # Iterate over the configurations:
    for config in configNames:
        # Change in the configuration's directory:
        os.chdir(config)
        if verbosityEnabled:
            print(analysingConfigMsg.format(config))

        # Gather all of the "run_<seed_number>" directories into a list:
        runDirs = [folderName for folderName in os.listdir() if folderName.startswith(runFolderStartPattern)]
        # Get the number of "run" folders:
        numRunDirs = len(runDirs)
        # Check if there were no run (result) directories found.
        # If there weren't, alert the user, and continue onto the
        # next configuration (if there is another):
        if numRunDirs == 0:
            print(noResultsForConfigMsg.format(config))
            os.chdir("../")
            continue
        # If the user has enabled verbosity, inform them of how
        # many run directories were found for the given configuration:
        if verbosityEnabled:
            print(runDirsForConfigMsg.format(numRunDirs, config))

        # ==== Iterate through the Run (Result) Directories ====
        for runDir in runDirs:
            # Change into the run directory:
            os.chdir(runDir)

            # Get the seed number from the run directory's name.
            # Do this by removing the 'run_' part of the name:
            seedNumber = runDir.replace(runFolderStartPattern, '')

            # Check if the log file or status file is present:
            if fastSearchRequested:
                statusFileFound = False
                if os.path.isdir(logFileNamePattern + "GOOD"):
                    statusFileFound = True
                    logFileName = logFileNamePattern + "GOOD"
                elif os.path.isdir(logFileNamePattern + "BAD"):
                    statusFileFound = True
                    logFileName = logFileNamePattern + "BAD"
                elif os.path.isdir(logFileNamePattern + "UNK"):
                    statusFileFound = True
                    logFileName = logFileNamePattern + "BAD"

            # If verbosity is enabled, alert the user of which
            # run (or seed) we are analsying:
            if verbosityEnabled:
                print(analysingRunDirMsg.format(runDir))


        os.chdir("../")

    exit()

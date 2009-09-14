#!/usr/bin/python

import sys, os, time, subprocess, re

PATCHING_RE = re.compile(r"patching file (.*)")
REJECT_RE = re.compile(r".*saving rejects to file (.*)")

PATCH_PARSE_ERROR = "The output from 'patch' was not able to be parsed"

def parse_patch_output(file_like):
    # I will document this properly when it is incorporated into the code.
    # This is a generator. The YIELD statements will return values to the
    # calling FOR loop, but maintain the internal state of the function. It's
    # a state machine, basically, and the RETURN statement signals an end state.
    
    # What is YIELDED: tuples of the form (filename, success, reject_file)
    # Reject file might be None. Errors in patch itself go unreported, unless
    # the calling function detects it. Alternatively, see [1] below.
    
    # The returned file names can be checked against the VCS information to see
    # if they need to be added. The success/failure flag is also useful for
    # reporting (or eg. not adding files that failed).
    
    # Returns:
    # (filename, success, reject file)
    
    # If the first line doesn't match, there was no output or patch is acting
    # funny. This is basically initialising the "state machine". Python has no
    # frickin' DO loop.
    
    line = file_like.readline()
    patch_match = PATCHING_RE.match(line)
    
    if patch_match:
        current_file = patch_match.group(1)
    else:
        # [1] NOTE: if the patch file is rubbish, we get here and never yield
        # anything (we end up at [2] below).
        # Alternatively, we could throw an exception here (realistically, a
        # rubbish patch is worthy of an exception, I feel). This can be caught
        # by the caller and reported sensibly to the user.
        current_file = None
        raise RuntimeError(PATCH_PARSE_ERROR)
    
    any_errors = False
    reject_file = None
    
    while current_file:
        
        # Read the next line        
        line = file_like.readline()
        
        # Does patch tell us we're starting a new file?
        patch_match = PATCHING_RE.match(line)
                
        # Starting a new file => that's it for the last one, so return the value
        # no line == end of patch output == same as above
        if patch_match or not line:
            
            yield (current_file, not any_errors, reject_file)
            
            if not line:
                # That's it from patch, so end the generator
                return
            
            # Starting a new file...
            current_file = patch_match.group(1)
            any_errors = False
            reject_file = None
        
        else:
            # Doesn't matter why we're here, anything else means ERROR
            
            any_errors = True
            
            reject_match = REJECT_RE.match(line)
            
            if reject_match:
                # Have current file, getting reject file info
                reject_file = reject_match.group(1)
            # else: we have an unknown error
    
    # [1] There is an implicit return here after the while loop ends.
    
if __name__ == "__main__":
    
    patch_file = sys.argv[1]

    # PATCH flags...
    # -N: always assume forward diff
    # -t: batch mode:
    #    skip patches whose headers do not contain file
    #    names (the same as -f); skip patches for which
    #    the file has the wrong version for the Prereq:
    #    line in the patch; and assume that patches are
    #    reversed if they look like they are.
    patch_proc = subprocess.Popen(["patch", 
                                   "-N", "-t", "-p0",
                                   "-i", str(patch_file),
                                   "--directory",
                                   os.getcwd()],
                                   
                              stdout = subprocess.PIPE,
                              stderr = subprocess.PIPE)
    
    print "Parsing patch file output"
    
    for file, success, rej_file in parse_patch_output(patch_proc.stdout):
        print
        print "File: %s" % file
        print "Success: %s" % success
        if rej_file: print "Reject file: %s" % rej_file
        

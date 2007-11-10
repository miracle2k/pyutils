"""
    Utilities for creating command line based scripts.
"""

# Some of the functionality in this module depends on "options", e.g. usually
# those are going to defined by script command line arguments. However, we do
# not deal with command line business, or argument parsing - do that any way
# you want. Just be sure to update these module-global options appropriately.
class Options(object):
    def __getattr__(self, name):
        # resolve all non-existing attributes to None
        return None
options = Options()

# common output functions - each represents a different "log level", and whether
# it ends up on the screen depends on arguments like verbose, quiet, etc.
#
# "verbose" and "message" return a boolean indicating whether the message was
# printed. "error" however returns an exit code.
def verbose(str):
    if options.verbose: print str
    return options.verbose
def message(str):
    if not options.quiet: print str
    return options.quiet
def error(str):
    print str
    return 1
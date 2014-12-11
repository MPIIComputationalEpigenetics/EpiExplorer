from __future__ import print_function  # Disable default print statement in place of function
import sys
import re
import os
import os.path
import time

# DO NOT import settings!
# This module was created to prevent a circular import references
# with settings/settings_default which uses readSettingsFile
# Issues with utilities.log usage here!!!


def getFileName(name, abs_name):
    if not os.path.isfile(name):
        ff = os.path.join(os.path.dirname(abs_name), name)

        if not os.path.isfile(ff):
            raise Exception("Error: No valid file name from " + name + " and " + abs_name)

        name = ff

    return os.path.abspath(name)



# TODO change this to use ConfigParser? Will current EpiExplorer section-less name=value ini's be valid?

def read_ini_file(file_path, raise_exception=True):
    """Reads an EpiExplorer ini/settings file and loads it into dictionary. Empty lines and lines
    beginning with # or ; will be ignored

    Args:
      file_name (str): File path
      raiseException (boolean, optional): Raise Exception if unlink fails. Defaults to True.

    Returns:
      dict: Key value pairs parsed from ini file

    Raises:
      IOError:   If file open fails
      Exception: If invalid line found
    """
    result = {}

    try:
        f = open(file_path)
    except IOError, e:

        if raise_exception:
            raise
        else:
            warning(e)
            return result

    # Pre-compile, although this will only save the in line re cache check
    line_re = re.compile('(.*)=(.*)')

    for line in f:    # Using implicit f.__iter__ method here
        line = line.strip()  # Remove flanking white space first

        if line and not (line.startswith("#") or line.startswith(";")):
            line_match = line_re.match(line)

            if line_match:
                result[line_match.group(1)] = line_match.group(2)
            else:
                raise Exception("Found invalid line in " + file_path + "\nLine:\t" + line)
    f.close()
    return result


def mkdir(path):
    if not os.path.isdir(path):
        print("Mkdir", path)
        os.mkdir(path)


def line_count(file_name):
    f = open(file_name)
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read  # loop optimization
    buf = read_f(buf_size)

    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    f.close()
    return lines


def downloadFile(url, local_file):
    if os.path.isfile(local_file):
        raise Exception("Error: File already exists " + local_file)

    from urllib import FancyURLopener

    class MyOpener(FancyURLopener):  # a special opener to simulate firefox queries
        version = 'Mozilla/5.0'

    myopener = MyOpener()
    myopener.retrieve(url, local_file)


def fileTimeStr(f):
    file_time = os.path.getctime(f)
    t = time.gmtime(file_time)
    s = time.strftime("%d %b %Y", t)
    return s


# Soft links could be to directories here
# Test using type(files) eq 'Type' or isinstance(obj, type)? or try for loop?
# Apparently not http://stackoverflow.com/questions/19684434/best-way-to-check-function-arguments-in-python
# Don't use assert either, but raise relevant Exception e.g. TypeError or ValueError if absolutely required
# Also issubclass(obj, class) or hasattr(var, 'attrname')


def rm_files(files, raise_exception=False):
    """Removes a list of files and optionally raises an Exception if it fails to unlink any of them

    Args:
      files (list|tuple): File paths.
      raiseException (boolean, optional): Raise Exception if unlink fails. Defaults to False.

    Returns:
      int: Number of files successfully removed.

    Raises:
      OSError:   If os.unlink fails and raiseException is specified
      Exception: If any of the path are not a file or a link
    """

    rmd_files = 0

    for file_path in files:

        if os.path.isfile(file_path) or os.path.islink(file_path):

            try:
                os.unlink(file_path)
                rmd_files += 1
            except OSError, ex:
                ex.strerror = "Failed to unlink file:\t" + file_path + "\n" + ex.errno + "\t" + ex.strerror

                if raise_exception:
                    raise
                else:
                    warning(ex)

        elif raise_exception:
            raise Exception("Failed to remove file as path is not a file or a link or does not exist:\t" + file_path)

        else:
            warning("Failed to remove file as path is not a file or a link or does not exist:\t" + file_path)
        # endif
    # endfor

    return rmd_files


def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)
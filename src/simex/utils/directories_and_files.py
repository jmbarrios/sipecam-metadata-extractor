import glob
import itertools

def multiple_file_types(input_directory, patterns, recursive=False):
    """
    Return iterable with files that have a common pattern. Will search
    in a recursive or non recursive way.
    Args:
        input_directory (str): directory where files with common pattern
        will be searched.
        patterns (list): list of patterns to search for.
    Returns:
        iterable with files that have a common pattern.
    """
    if recursive:
        expression = "/**/*"
    else:
        expression = "/*"
    return itertools.chain.from_iterable(glob.iglob(input_directory + \
                                                    expression + pattern,
                                                    recursive=recursive) for pattern in patterns)
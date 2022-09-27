from pathlib import Path

def multiple_file_types(input_directory: str,
                        patterns: list[str],
                        recursive: bool=False) -> list[str]:
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
        expression = "**/*"
    else:
        expression = "*"

    return [str(file) for file in Path(input_directory).glob(expression) if
            file.suffix in patterns]

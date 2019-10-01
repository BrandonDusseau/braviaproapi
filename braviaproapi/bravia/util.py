def coalesce_none_or_empty(input_string):
    '''
    Returns the input string or None if it is empty.

    Args:
        input_string (str or None): The string to process.

    Returns:
        The input string or `None` if it is empty.
    '''

    if not input_string:
        return None
    else:
        return input_string

def multiversion_regex_builder(versions):
    """Generates a regex string from a list of versions.

    Every documentation project `conf.py` file uses this function
    to define the different documentation versions supported.

    :param versions: A list of versions. Versions could be either branch names or tags.
    :type versions: list of str

    :return: The equivalent regular expression.
    :rtype: str
    """

    if len(versions) == 0:
        return "None"
    elif len(versions) == 1 and versions[0] == "*":
        return r"^.*"
    elif len(versions) == 1:
        return r"^" + versions[0] + r"$"
    else:
        return r"\b(" + "|".join(versions) + r")\b"

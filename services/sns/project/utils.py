import re


# From this response in Stackoverflow
# http://stackoverflow.com/a/1176023/1072990
def to_snake_case(camel_str):
    """Convert CamelCase or mixedCase into snake_case."""
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()

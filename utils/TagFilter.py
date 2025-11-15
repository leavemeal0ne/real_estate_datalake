import re
from config.config import FLAT_BASE_PATTERN

def flat_filter(tag):
    if (
            tag.has_attr('class')
            and len(tag['class']) == 1
            and len(re.findall(FLAT_BASE_PATTERN, tag['class'][0])) == 1
        ):
        return True
    return False
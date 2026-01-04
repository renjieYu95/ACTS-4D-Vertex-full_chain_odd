import re
import itertools

def get_event_details(event_label):
    m = re.match(r"ttbar_pu(\d+)", event_label)
    if m:
        pu = int(m.group(1))
        return "ttbar", {"pu": pu}


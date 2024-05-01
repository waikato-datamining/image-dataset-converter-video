from typing import List, Dict


def list_classes() -> Dict[str, List[str]]:
    return {
        "seppl.io.Reader": [
            "idc.video.reader",
        ],
        "seppl.io.Filter": [
            "idc.video.filter",
        ],
        "seppl.io.Writer": [
            "idc.video.writer",
        ],
    }

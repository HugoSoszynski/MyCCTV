from typing import Dict


class Plugin(object):

    def hooks(self) -> Dict[str, object]:
        raise NotImplementedError


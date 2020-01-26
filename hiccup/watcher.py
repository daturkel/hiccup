import logging
from typing import Union, Optional, List
from watchgod import DefaultDirWatcher
from wcmatch.pathlib import Path, GLOBSTAR

from .utils import listify


class GlobWatcher(DefaultDirWatcher):
    def __init__(
        self,
        root_path,
        match_patterns: Optional[List[str]] = None,
        skip_patterns: Optional[List[str]] = None,
    ):
        if match_patterns is None:
            # can't use empty list as default, so we use catch-all pattern
            self.match_patterns = ["**/*"]
        else:
            self.match_patterns = match_patterns
        self.skip_patterns = listify(skip_patterns)
        super().__init__(root_path)

    def should_watch_file(self, entry):
        entry = Path(entry)
        return any(
            entry.globmatch(pattern, flags=GLOBSTAR) for pattern in self.match_patterns
        ) and not any(
            entry.globmatch(pattern, flags=GLOBSTAR) for pattern in self.skip_patterns
        )

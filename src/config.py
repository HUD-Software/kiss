class Config:
    def __init__(self, is_release: bool = False, is_debug_info: bool = True):
        self._is_release = is_release
        self._debug_info = is_debug_info

    @property
    def is_release(self) -> bool:
        return self._is_release
    @property
    def is_debug_info(self) -> bool:
        return self._debug_info
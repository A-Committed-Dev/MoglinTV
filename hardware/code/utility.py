class Timer:
    def __init__(self, duration: float = 0):
        self._deadline = 0.0
        self._duration = duration

    def start(self, duration: float | None = None):
        self._deadline = time.monotonic() + (duration if duration is not None else self._duration)

    def expired(self) -> bool:
        return self._deadline > 0 and time.monotonic() >= self._deadline

    def active(self) -> bool:
        return self._deadline > 0 and time.monotonic() < self._deadline

    def reset(self):
        self._deadline = 0.0

    def elapsed(self) -> float:
        if self._deadline <= 0:
            return 0.0
        return time.monotonic() - (self._deadline - self._duration)
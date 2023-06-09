from __future__ import annotations

import threading


class CmpHandleBase():
    def __init__(self, next: CmpHandleBase, cmp) -> None:
        self.next = next
        self.cmp = cmp
        self.event = threading.Event()

    def handle(self, event):
        processed = False
        handler = f"handle_{event}"

        if hasattr(self, handler):
            methond = getattr(self, handler)
            processed = methond(event)

        if hasattr(self, "handle_default"):
            processed = self.handle_default(event)

        if self.next and not processed:
            processed = self.next.handle(event)

        return processed

    def wait(self, timeOut=None):
        ret = self.event.wait(timeOut)
        return ret
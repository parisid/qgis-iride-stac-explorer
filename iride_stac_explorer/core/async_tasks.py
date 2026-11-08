# -*- coding: utf-8 -*-
from typing import Callable, Any
from qgis.core import QgsTask

class AsyncWorkerTask(QgsTask):
    """Task generico in background per operazioni di rete asincrone (STAC search, collections, signer, thumbnail)."""

    def __init__(self, description: str, worker_func: Callable[[], Any], on_finished: Callable[[Any, Exception], None]):
        can_cancel_flag = getattr(getattr(QgsTask, "Flag", None), "CanCancel", getattr(QgsTask, "CanCancel", 1))
        super().__init__(description, can_cancel_flag)
        self.worker_func = worker_func
        self.on_finished = on_finished
        self.result = None
        self.exception = None

    def run(self) -> bool:
        try:
            if self.isCanceled():
                return False
            self.result = self.worker_func()
            return not self.isCanceled()
        except Exception as e:
            self.exception = e
            return False

    def finished(self, result: bool):
        if self.on_finished:
            self.on_finished(self.result, self.exception)


class DownloadAssetTask(QgsTask):
    """Task in background dedicato al download di file binari con tracciamento della percentuale."""

    def __init__(self, description: str, download_func: Callable[[Callable[[float], bool]], Any], on_finished: Callable[[Any, Exception], None]):
        can_cancel_flag = getattr(getattr(QgsTask, "Flag", None), "CanCancel", getattr(QgsTask, "CanCancel", 1))
        super().__init__(description, can_cancel_flag)
        self.download_func = download_func
        self.on_finished = on_finished
        self.result = None
        self.exception = None

    def run(self) -> bool:
        try:
            def _progress(pct: float) -> bool:
                if self.isCanceled():
                    return False
                self.setProgress(pct)
                return True

            self.result = self.download_func(_progress)
            return not self.isCanceled()
        except Exception as e:
            self.exception = e
            return False

    def finished(self, result: bool):
        if self.on_finished:
            self.on_finished(self.result, self.exception)

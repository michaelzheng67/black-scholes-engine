'''
Custom thread class that makes it easier to "kill" threads scheduled to do work
in an infinite loop. Signalled threads trigger a stop event which stop execution.
Note: start - join synchronization replaced by start - signal.
'''

import threading

class WorkerThread(threading.Thread):

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.stop_event = threading.Event()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        
        while not self.stop_event.is_set():
            self.func(*self.args, **self.kwargs)

    def signal(self):
        self.stop_event.set()
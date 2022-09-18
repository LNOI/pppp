import threading
from typing import Callable, Dict, Any

def schedule_parallel_task(func:Callable, *args, **kwargs:Dict[str, Any]) -> None:
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.start()
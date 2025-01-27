import asyncio
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_rate: int, time_period: int):
        self.max_rate = max_rate
        self.time_period = time_period
        self.calls = deque()
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        async with self._lock:
            now = time.time()
            
            # Remove old calls
            while self.calls and now - self.calls[0] > self.time_period:
                self.calls.popleft()
                
            if len(self.calls) >= self.max_rate:
                sleep_time = self.calls[0] + self.time_period - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
            self.calls.append(now)
            return self
            
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass 
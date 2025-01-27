import openai
from config import Config
import logging
import asyncio
from collections import deque
import time

logger = logging.getLogger(__name__)

class OpenAIConfigError(Exception):
    """Raised when OpenAI configuration is invalid or incomplete."""
    pass

class OpenAIAssistant:
    def __init__(self):
        # Validate required configuration
        self._validate_config()
        
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
        self.temperature = Config.OPENAI_TEMPERATURE
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.calls = deque()
        self._lock = asyncio.Lock()
        self.max_rate = 50  # requests per minute
        self.time_period = 60  # seconds
        
    def _validate_config(self):
        """Validate OpenAI configuration settings."""
        if not hasattr(Config, 'OPENAI_API_KEY') or not Config.OPENAI_API_KEY:
            raise OpenAIConfigError("OpenAI API key is missing")
            
        if not hasattr(Config, 'OPENAI_MODEL') or not Config.OPENAI_MODEL:
            raise OpenAIConfigError("OpenAI model configuration is missing")
            
        if not hasattr(Config, 'OPENAI_TEMPERATURE'):
            raise OpenAIConfigError("OpenAI temperature configuration is missing")
        
        try:
            temp = float(Config.OPENAI_TEMPERATURE)
            if not 0 <= temp <= 2:
                raise OpenAIConfigError("OpenAI temperature must be between 0 and 2")
        except (ValueError, TypeError):
            raise OpenAIConfigError("OpenAI temperature must be a valid number")
            
        if not hasattr(Config, 'OPENAI_MAX_TOKENS'):
            raise OpenAIConfigError("OpenAI max_tokens configuration is missing")
            
        try:
            tokens = int(Config.OPENAI_MAX_TOKENS)
            if tokens <= 0:
                raise OpenAIConfigError("OpenAI max_tokens must be a positive integer")
        except (ValueError, TypeError):
            raise OpenAIConfigError("OpenAI max_tokens must be a valid integer")

    async def _check_rate_limit(self):
        async with self._lock:
            now = time.time()
            while self.calls and now - self.calls[0] > self.time_period:
                self.calls.popleft()
                
            if len(self.calls) >= self.max_rate:
                sleep_time = self.calls[0] + self.time_period - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
            self.calls.append(now)
        
    async def gpt_4_min_response(self, prompt):
        await self._check_rate_limit()
        try:
            response = openai.ChatCompletion.create(
                messages=prompt,
                model=self.model,
                temperature=self.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def gpt_4_response(self, prompt):
        await self._check_rate_limit()
        try:
            response = openai.ChatCompletion.create(
                messages=prompt,
                model=self.model,
                temperature=self.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
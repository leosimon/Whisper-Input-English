import os
import threading
import time
from functools import wraps

import dotenv
import httpx
from openai import OpenAI
from opencc import OpenCC

from ..llm.symbol import SymbolProcessor
from ..utils.logger import logger

dotenv.load_dotenv()

def timeout_decorator(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            error = [None]
            completed = threading.Event()

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    error[0] = e
                finally:
                    completed.set()

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

            if completed.wait(seconds):
                if error[0] is not None:
                    raise error[0]
                return result[0]
            raise TimeoutError(f"Timeout ({seconds}秒)")

        return wrapper
    return decorator

class WhisperProcessor:
    # Class-level configuration parameters
    DEFAULT_TIMEOUT = 20  # API timeout (seconds)
    DEFAULT_MODEL = None
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        base_url = os.getenv("GROQ_BASE_URL")
        self.convert_to_simplified = os.getenv("CONVERT_TO_SIMPLIFIED", "false").lower() == "true"
        self.cc = OpenCC('t2s') if self.convert_to_simplified else None
        self.symbol = SymbolProcessor()
        self.add_symbol = os.getenv("ADD_SYMBOL", "false").lower() == "true"
        self.optimize_result = os.getenv("OPTIMIZE_RESULT", "false").lower() == "true"
        self.timeout_seconds = self.DEFAULT_TIMEOUT
        self.service_platform = os.getenv("SERVICE_PLATFORM", "groq").lower()

        if self.service_platform == "groq":
            assert api_key, "GROQ_API_KEY environment variable not set"
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url if base_url else None
            )
            self.DEFAULT_MODEL = "whisper-large-v3-turbo"
        elif self.service_platform == "siliconflow":
            assert api_key, "SILICONFLOW_API_KEY environment variable not set"
            self.DEFAULT_MODEL = "FunAudioLLM/SenseVoiceSmall"
        else:
            raise ValueError(f"Unknown platform: {self.service_platform}")

    def _convert_traditional_to_simplified(self, text):
        """Convert Traditional Chinese to Simplified Chinese"""
        if not self.convert_to_simplified or not text:
            return text
        return self.cc.convert(text)
    
    @timeout_decorator(10)
    def _call_whisper_api(self, mode, audio_data, prompt):
        """Call Whisper API"""
        if mode == "translations":
            response = self.client.audio.translations.create(
                model="whisper-large-v3",
                response_format="text",
                prompt=prompt,
                file=("audio.wav", audio_data)
            )
        else:  # transcriptions
            response = self.client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                response_format="text",
                prompt=prompt,
                file=("audio.wav", audio_data)
            )
        return str(response).strip()

    def process_audio(self, audio_buffer, mode="transcriptions", prompt=""):
        """Process audio using Whisper API (transcription or translation)
        
        Args:
            audio_path: Audio file path
            mode: 'transcriptions' or 'translations', determines whether to transcribe or translate
            prompt: Prompt text
        
        Returns:
            tuple: (result text, error message)
            - If successful, error message is None
            - If failed, result text is None
        """
        try:
            start_time = time.time()

            logger.info(f"Calling Whisper API... (mode: {mode})")
            result = self._call_whisper_api(mode, audio_buffer, prompt)

            logger.info(f"API call successful ({mode}), time taken: {time.time() - start_time:.1f} seconds")
            result = self._convert_traditional_to_simplified(result)
            logger.info(f"Recognition result: {result}")
            
            # Only add punctuation symbols when using groq API
            if self.service_platform == "groq" and self.add_symbol:
                result = self.symbol.add_symbol(result)
                logger.info(f"Added punctuation symbols: {result}")
            if self.optimize_result:
                result = self.symbol.optimize_result(result)
                logger.info(f"Optimized result: {result}")

            return result, None
            

        except TimeoutError:
            error_msg = f"❌ API request timeout ({self.timeout_seconds} seconds)"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"❌ {str(e)}"
            logger.error(f"Audio processing error: {str(e)}", exc_info=True)
            return None, error_msg
        finally:
            audio_buffer.close()  # Explicitly close byte stream
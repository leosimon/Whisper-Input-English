import os
import threading
import time
from functools import wraps

import dotenv
import httpx

from src.llm.translate import TranslateProcessor
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
            raise TimeoutError(f"Operation timeout ({seconds} seconds)")

        return wrapper
    return decorator

class SenseVoiceSmallProcessor:
    # Class-level configuration parameters
    DEFAULT_TIMEOUT = 20  # API timeout (seconds)
    DEFAULT_MODEL = "FunAudioLLM/SenseVoiceSmall"
    
    def __init__(self):
        api_key = os.getenv("SILICONFLOW_API_KEY")
        assert api_key, "SILICONFLOW_API_KEY environment variable not set"
        
        self.convert_to_simplified = os.getenv("CONVERT_TO_SIMPLIFIED", "false").lower() == "true"
        # self.cc = OpenCC('t2s') if self.convert_to_simplified else None
        # self.symbol = SymbolProcessor()
        # self.add_symbol = os.getenv("ADD_SYMBOL", "false").lower() == "true"
        # self.optimize_result = os.getenv("OPTIMIZE_RESULT", "false").lower() == "true"
        self.timeout_seconds = self.DEFAULT_TIMEOUT
        self.translate_processor = TranslateProcessor()

    def _convert_traditional_to_simplified(self, text):
        """Convert Traditional Chinese to Simplified Chinese"""
        if not self.convert_to_simplified or not text:
            return text
        return self.cc.convert(text)

    @timeout_decorator(10)
    def _call_api(self, audio_data):
        """Call SiliconFlow API"""
        transcription_url = "https://api.siliconflow.cn/v1/audio/transcriptions"
        
        files = {
            'file': ('audio.wav', audio_data),
            'model': (None, self.DEFAULT_MODEL)
        }

        headers = {
            'Authorization': f"Bearer {os.getenv('SILICONFLOW_API_KEY')}"
        }

        with httpx.Client() as client:
            response = client.post(transcription_url, files=files, headers=headers)
            response.raise_for_status()
            return response.json().get('text', 'Failed to get result')


    def process_audio(self, audio_buffer, mode="transcriptions", prompt=""):
        """Process audio (transcription or translation)
        
        Args:
            audio_buffer: Audio data buffer
            mode: 'transcriptions' or 'translations', determines whether to transcribe or translate
        
        Returns:
            tuple: (result text, error message)
            - If successful, error message is None
            - If failed, result text is None
        """
        try:
            start_time = time.time()
            
            logger.info(f"Calling SiliconFlow API... (mode: {mode})")
            result = self._call_api(audio_buffer)

            logger.info(f"API call successful ({mode}), time taken: {time.time() - start_time:.1f} seconds")
            # result = self._convert_traditional_to_simplified(result)
            if mode == "translations":
                result = self.translate_processor.translate(result)
            logger.info(f"Recognition result: {result}")
            
            # if self.add_symbol:
            #     result = self.symbol.add_symbol(result)
            #     logger.info(f"Added punctuation symbols: {result}")
            # if self.optimize_result:
            #     result = self.symbol.optimize_result(result)
            #     logger.info(f"Optimized result: {result}")

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

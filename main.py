import os
import sys

from dotenv import load_dotenv

load_dotenv()

from src.audio.recorder import AudioRecorder
from src.keyboard.listener import KeyboardManager, check_accessibility_permissions
from src.transcription.whisper import WhisperProcessor
from src.utils.logger import logger
from src.transcription.senseVoiceSmall import SenseVoiceSmallProcessor


def check_microphone_permissions():
    """Check microphone permissions and provide guidance"""
    logger.warning("\n=== macOS Microphone Permission Check ===")
    logger.warning("This application requires microphone access to record audio.")
    logger.warning("\nPlease follow these steps to grant permission:")
    logger.warning("1. Open System Preferences")
    logger.warning("2. Click Privacy & Security")
    logger.warning("3. Click Microphone on the left")
    logger.warning("4. Click the lock icon at the bottom right and enter your password")
    logger.warning("5. In the list on the right, find Terminal (or your terminal app) and check it")
    logger.warning("\nAfter granting permission, please rerun this program.")
    logger.warning("===============================\n")

class VoiceAssistant:
    def __init__(self, audio_processor):
        self.audio_recorder = AudioRecorder()
        self.audio_processor = audio_processor
        self.keyboard_manager = KeyboardManager(
            on_record_start=self.start_transcription_recording,
            on_record_stop=self.stop_transcription_recording,
            on_translate_start=self.start_translation_recording,
            on_translate_stop=self.stop_translation_recording,
            on_reset_state=self.reset_state
        )
    
    def start_transcription_recording(self):
        """Start recording (transcription mode)"""
        self.audio_recorder.start_recording()
    
    def stop_transcription_recording(self):
        """Stop recording and process (transcription mode)"""
        audio = self.audio_recorder.stop_recording()
        if audio == "TOO_SHORT":
            logger.warning("Recording is too short, state will be reset")
            self.keyboard_manager.reset_state()
        elif audio:
            result = self.audio_processor.process_audio(
                audio,
                mode="transcriptions",
                prompt=""
            )
            # Unpack return value
            text, error = result if isinstance(result, tuple) else (result, None)
            self.keyboard_manager.type_text(text, error)
        else:
            logger.error("No audio data, state will be reset")
            self.keyboard_manager.reset_state()
    
    def start_translation_recording(self):
        """Start recording (translation mode)"""
        self.audio_recorder.start_recording()
    
    def stop_translation_recording(self):
        """Stop recording and process (translation mode)"""
        audio = self.audio_recorder.stop_recording()
        if audio == "TOO_SHORT":
            logger.warning("Recording is too short, state will be reset")
            self.keyboard_manager.reset_state()
        elif audio:
            result = self.audio_processor.process_audio(
                    audio,
                    mode="translations",
                    prompt=""
                )
            text, error = result if isinstance(result, tuple) else (result, None)
            self.keyboard_manager.type_text(text,error)
        else:
            logger.error("No audio data, state will be reset")
            self.keyboard_manager.reset_state()

    def reset_state(self):
        """Reset state"""
        self.keyboard_manager.reset_state()
    
    def run(self):
        """Run voice assistant"""
        logger.info("=== Voice Assistant Started ===")
        self.keyboard_manager.start_listening()

def main():
    # Determine whether to use Whisper or SiliconFlow
    service_platform = os.getenv("SERVICE_PLATFORM", "siliconflow")
    if service_platform == "groq":
        audio_processor = WhisperProcessor()
    elif service_platform == "siliconflow":
        audio_processor = SenseVoiceSmallProcessor()
    else:
        raise ValueError(f"Invalid service platform: {service_platform}")
    try:
        assistant = VoiceAssistant(audio_processor)
        assistant.run()
    except Exception as e:
        error_msg = str(e)
        if "Input event monitoring will not be possible" in error_msg:
            check_accessibility_permissions()
            sys.exit(1)
        elif "Unable to access audio device" in error_msg:
            check_microphone_permissions()
            sys.exit(1)
        else:
            logger.error(f"Error occurred: {error_msg}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    main() 
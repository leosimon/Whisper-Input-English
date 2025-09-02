from pynput.keyboard import Controller, Key, Listener
import pyperclip
from ..utils.logger import logger
import time
from .inputState import InputState
import os


class KeyboardManager:
    def __init__(self, on_record_start, on_record_stop, on_translate_start, on_translate_stop, on_reset_state):
        self.keyboard = Controller()
        self.option_pressed = False
        self.shift_pressed = False
        self.temp_text_length = 0  # 用于跟踪临时文本的长度
        self.processing_text = None  # 用于跟踪正在处理的文本
        self.error_message = None  # 用于跟踪错误信息
        self.warning_message = None  # 用于跟踪警告信息
        self.option_press_time = None  # 记录 Option 按下的时间戳
        self.PRESS_DURATION_THRESHOLD = 0.5  # 按键持续时间阈值（秒）
        self.is_checking_duration = False  # 用于控制定时器线程
        self.has_triggered = False  # 用于防止重复触发
        self._original_clipboard = None  # 保存原始剪贴板内容
        
        
        # 回调函数
        self.on_record_start = on_record_start
        self.on_record_stop = on_record_stop
        self.on_translate_start = on_translate_start
        self.on_translate_stop = on_translate_stop
        self.on_reset_state = on_reset_state

        
        # State management
        self._state = InputState.IDLE
        self._state_messages = {
            InputState.IDLE: "",
            InputState.RECORDING: "🎤 Recording...",
            InputState.RECORDING_TRANSLATE: "🎤 Recording (Translation Mode)",
            InputState.PROCESSING: "🔄 Transcribing...",
            InputState.TRANSLATING: "🔄 Translating...",
            InputState.ERROR: lambda msg: f"{msg}",  # Error messages use function to generate dynamically
            InputState.WARNING: lambda msg: f"⚠️ {msg}"  # Warning messages use function to generate dynamically
        }

        # Get system platform
        sysetem_platform = os.getenv("SYSTEM_PLATFORM")
        if sysetem_platform == "win" :
            self.sysetem_platform = Key.ctrl
            logger.info("Configured for Windows platform")
        else:
            self.sysetem_platform = Key.cmd
            logger.info("Configured for Mac platform")
        

        # Get transcription and translation buttons
        transcriptions_button = os.getenv("TRANSCRIPTIONS_BUTTON")
        try:
            self.transcriptions_button = Key[transcriptions_button]
            logger.info(f"Configured transcription button: {transcriptions_button}")
        except KeyError:
            logger.error(f"Invalid transcription button configuration: {transcriptions_button}")

        translations_button = os.getenv("TRANSLATIONS_BUTTON")
        try:
            self.translations_button = Key[translations_button]
            logger.info(f"Configured translation button (combined with transcription button): {translations_button}")
        except KeyError:
            logger.error(f"Invalid translation button configuration: {translations_button}")

        logger.info(f"Hold {transcriptions_button} key: Real-time speech transcription (keep original text)")
        logger.info(f"Hold {translations_button} + {transcriptions_button} key: Real-time speech translation (translate to English)")
    
    @property
    def state(self):
        """Get current state"""
        return self._state
    
    @state.setter
    def state(self, new_state):
        """Set new state and update UI"""
        if new_state != self._state:
            self._state = new_state
            
            # Get state message
            message = self._state_messages[new_state]
            
            # Display different messages based on state transition type
            match new_state:
                case InputState.RECORDING :
                    # Recording state
                    self.temp_text_length = 0
                    self.type_temp_text(message)
                    self.on_record_start()
                    
                
                case InputState.RECORDING_TRANSLATE:
                    # Translation and recording state
                    self.temp_text_length = 0
                    self.type_temp_text(message)
                    self.on_translate_start()

                case InputState.PROCESSING:
                    self._delete_previous_text()
                    self.type_temp_text(message)
                    self.processing_text = message
                    self.on_record_stop()

                case InputState.TRANSLATING:
                    # Translation state
                    self._delete_previous_text()                 
                    self.type_temp_text(message)
                    self.processing_text = message
                    self.on_translate_stop()
                
                case InputState.WARNING:
                    # Warning state
                    message = message(self.warning_message)
                    self._delete_previous_text()
                    self.type_temp_text(message)
                    self.warning_message = None
                    self._schedule_message_clear()     
                
                case InputState.ERROR:
                    # Error state
                    message = message(self.error_message)
                    self._delete_previous_text()
                    self.type_temp_text(message)
                    self.error_message = None
                    self._schedule_message_clear()  
            
                case InputState.IDLE:
                    # Idle state, clear all temporary text
                    self.processing_text = None
                
                case _:
                    # Other states
                    self.type_temp_text(message)
    
    def _schedule_message_clear(self):
        """Schedule message clearing"""
        def clear_message():
            time.sleep(2)  # Warning message displays for 2 seconds
            self.state = InputState.IDLE
        
        import threading
        threading.Thread(target=clear_message, daemon=True).start()
    
    def show_warning(self, warning_message):
        """Show warning message"""
        self.warning_message = warning_message
        self.state = InputState.WARNING
    
    def show_error(self, error_message):
        """Show error message"""
        self.error_message = error_message
        self.state = InputState.ERROR
    
    def _save_clipboard(self):
        """保存当前剪贴板内容"""
        if self._original_clipboard is None:
            self._original_clipboard = pyperclip.paste()

    def _restore_clipboard(self):
        """Restore original clipboard content"""
        if self._original_clipboard is not None:
            pyperclip.copy(self._original_clipboard)
            self._original_clipboard = None

    def type_text(self, text, error_message=None):
        """将文字输入到当前光标位置
        
        Args:
            text: 要输入的文本或包含文本和错误信息的元组
            error_message: 错误信息
        """
        # 如果text是元组，说明是从process_audio返回的结果
        if isinstance(text, tuple):
            text, error_message = text
            
        if error_message:
            self.show_error(error_message)
            return
            
        if not text:
            # If no text and no error, it might be insufficient recording duration
            if self.state in (InputState.PROCESSING, InputState.TRANSLATING):
                self.show_warning("Recording duration too short, please record for at least 1 second")
            return
            
        try:
            logger.info("Inputting transcription text...")
            self._delete_previous_text()
            
            # First input text and completion mark
            self.type_temp_text(text+" ✅")
            
            # Wait a short time to ensure text is input
            time.sleep(0.5)
            
            # Delete completion mark (2 characters: space and ✅)
            self.temp_text_length = 2
            self._delete_previous_text()
            
            # Copy transcription result to clipboard
            if os.getenv("KEEP_ORIGINAL_CLIPBOARD", "true").lower() != "true":
                pyperclip.copy(text)
            else:
                # Restore original clipboard content
                self._restore_clipboard()
            
            logger.info("Text input completed")
            
            # Clear processing state
            self.state = InputState.IDLE
        except Exception as e:
            logger.error(f"Text input failed: {e}")
            self.show_error(f"❌ Text input failed: {e}")
    
    def _delete_previous_text(self):
        """Delete previously entered temporary text"""
        if self.temp_text_length > 0:
            for _ in range(self.temp_text_length):
                self.keyboard.press(Key.backspace)
                self.keyboard.release(Key.backspace)

        self.temp_text_length = 0
    
    def type_temp_text(self, text):
        """Input temporary status text"""
        if not text:
            return
            
        # Copy text to clipboard
        pyperclip.copy(text)

        # Simulate Ctrl + V to paste text
        with self.keyboard.pressed(self.sysetem_platform):
            self.keyboard.press('v')
            self.keyboard.release('v')

        # Update temporary text length
        self.temp_text_length = len(text)
    
    def start_duration_check(self):
        """Start checking key press duration"""
        if self.is_checking_duration:
            return

        def check_duration():
            while self.is_checking_duration and self.option_pressed:
                current_time = time.time()
                if (not self.has_triggered and 
                    self.option_press_time and 
                    (current_time - self.option_press_time) >= self.PRESS_DURATION_THRESHOLD):
                    
                    # Trigger corresponding function when threshold is reached
                    if self.option_pressed and self.shift_pressed and self.state.can_start_recording:
                        self.state = InputState.RECORDING_TRANSLATE
                        # self.on_translate_start()
                        self.has_triggered = True
                    elif self.option_pressed and not self.shift_pressed and self.state.can_start_recording:
                        self.state = InputState.RECORDING
                        # self.on_record_start()
                        self.has_triggered = True
                
                time.sleep(0.01)  # Brief sleep to reduce CPU usage

        self.is_checking_duration = True
        import threading
        threading.Thread(target=check_duration, daemon=True).start()

    def on_press(self, key):
        """Callback when key is pressed"""
        try:
            if key == self.transcriptions_button: #Key.f8:  # Option key pressed
                # Save clipboard content before starting any operation
                if self._original_clipboard is None:
                    self._original_clipboard = pyperclip.paste()
                    
                self.option_pressed = True
                self.option_press_time = time.time()
                self.start_duration_check()
            elif key == self.translations_button:
                self.shift_pressed = True
        except AttributeError:
            pass

    def on_release(self, key):
        """按键释放时的回调"""
        try:
            if key == self.transcriptions_button:# Key.f8:  # Option 键释放
                self.shift_pressed = False
                self.option_pressed = False
                self.option_press_time = None
                self.is_checking_duration = False
                
                if self.has_triggered:
                    if self.state == InputState.RECORDING_TRANSLATE:
                        self.state = InputState.TRANSLATING
                    elif self.state == InputState.RECORDING:
                        self.state = InputState.PROCESSING
                    self.has_triggered = False
            elif key == self.translations_button:#Key.f7:
                self.shift_pressed = False
                if (self.state == InputState.RECORDING_TRANSLATE and 
                    not self.option_pressed and 
                    self.has_triggered):
                    self.state = InputState.TRANSLATING
                    self.has_triggered = False
        except AttributeError:
            pass
    
    def start_listening(self):
        """开始监听键盘事件"""
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def reset_state(self):
        """重置所有状态和临时文本"""
        # 清除临时文本
        self._delete_previous_text()
        
        # 恢复剪贴板
        self._restore_clipboard()
        
        # 重置状态标志
        self.option_pressed = False
        self.shift_pressed = False
        self.option_press_time = None
        self.is_checking_duration = False
        self.has_triggered = False
        self.processing_text = None
        self.error_message = None
        self.warning_message = None
        
        # Set to idle state
        self.state = InputState.IDLE

def check_accessibility_permissions():
    """检查是否有辅助功能权限并提供指导"""
    logger.warning("\n=== macOS 辅助功能权限检查 ===")
    logger.warning("此应用需要辅助功能权限才能监听键盘事件。")
    logger.warning("\n请按照以下步骤授予权限：")
    logger.warning("1. 打开 系统偏好设置")
    logger.warning("2. 点击 隐私与安全性")
    logger.warning("3. 点击左侧的 辅助功能")
    logger.warning("4. 点击右下角的锁图标并输入密码")
    logger.warning("5. 在右侧列表中找到 Terminal（或者您使用的终端应用）并勾选")
    logger.warning("\n授权后，请重新运行此程序。")
    logger.warning("===============================\n") 

from enum import Enum, auto

class InputState(Enum):
    """Input state enumeration"""
    IDLE = auto()           # Idle state
    RECORDING = auto()      # Recording
    RECORDING_TRANSLATE = auto()  # Recording (translation mode)
    PROCESSING = auto()     # Processing
    TRANSLATING = auto()    # Translating
    ERROR = auto()          # Error state
    WARNING = auto()        # Warning state (for insufficient recording duration, etc.)

    @property
    def is_recording(self):
        """Check if in recording state"""
        return self in (InputState.RECORDING, InputState.RECORDING_TRANSLATE)
    
    @property
    def can_start_recording(self):
        """检查是否可以开始新的录音"""
        return not self.is_recording

import io
import sounddevice as sd
import numpy as np
import queue
import soundfile as sf
import os
import tempfile
from ..utils.logger import logger
import time

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        # self.temp_dir = tempfile.mkdtemp()
        self.current_device = None
        self.record_start_time = None
        self.min_record_duration = 1.0  # Minimum recording duration (seconds)
        self._check_audio_devices()
        # logger.info(f"Initialization complete, temporary file directory: {self.temp_dir}")
        logger.info(f"Initialization complete")
    
    def _list_audio_devices(self):
        """List all available audio input devices"""
        devices = sd.query_devices()
        logger.info("\n=== Available Audio Input Devices ===")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:  # Only show input devices
                status = "Default Device ✓" if device['name'] == self.current_device else ""
                logger.info(f"{i}: {device['name']} "
                          f"(Sample Rate: {int(device['default_samplerate'])}Hz, "
                          f"Channels: {device['max_input_channels']}) {status}")
        logger.info("========================\n")
    
    def _check_audio_devices(self):
        """检查音频设备状态"""
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            self.current_device = default_input['name']
            
            logger.info("\n=== Current Audio Device Information ===")
            logger.info(f"Default Input Device: {self.current_device}")
            logger.info(f"Supported Sample Rate: {int(default_input['default_samplerate'])}Hz")
            logger.info(f"Max Input Channels: {default_input['max_input_channels']}")
            logger.info("========================\n")
            
            # If default sample rate differs from ours, use device's default sample rate
            if abs(default_input['default_samplerate'] - self.sample_rate) > 100:
                self.sample_rate = int(default_input['default_samplerate'])
                logger.info(f"Adjusted sample rate to: {self.sample_rate}Hz")
            
            # List all available devices
            self._list_audio_devices()
            
        except Exception as e:
            logger.error(f"Error checking audio devices: {e}")
            raise RuntimeError("Unable to access audio device, please check system permission settings")
    
    def _check_device_changed(self):
        """检查默认音频设备是否发生变化"""
        try:
            default_input = sd.query_devices(kind='input')
            if default_input['name'] != self.current_device:
                logger.warning(f"\nAudio device has switched:")
                logger.warning(f"From: {self.current_device}")
                logger.warning(f"To: {default_input['name']}\n")
                self.current_device = default_input['name']
                self._check_audio_devices()
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking device changes: {e}")
            return False
    
    def start_recording(self):
        """Start recording"""
        if not self.recording:
            try:
                # Check if device has changed
                self._check_device_changed()
                
                logger.info("Starting recording...")
                self.recording = True
                self.record_start_time = time.time()
                self.audio_data = []
                
                def audio_callback(indata, frames, time, status):
                    if status:
                        logger.warning(f"Audio recording status: {status}")
                    if self.recording:
                        self.audio_queue.put(indata.copy())
                
                self.stream = sd.InputStream(
                    channels=1,
                    samplerate=self.sample_rate,
                    callback=audio_callback,
                    device=None,  # Use default device
                    latency='low'  # Use low latency mode
                )
                self.stream.start()
                logger.info(f"Audio stream started (device: {self.current_device})")
            except Exception as e:
                self.recording = False
                logger.error(f"Failed to start recording: {e}")
                raise
    
    def stop_recording(self):
        """Stop recording and return audio data"""
        if not self.recording:
            return None
            
        logger.info("Stopping recording...")
        self.recording = False
        self.stream.stop()
        self.stream.close()
        
        # Check recording duration
        if self.record_start_time:
            record_duration = time.time() - self.record_start_time
            if record_duration < self.min_record_duration:
                logger.warning(f"Recording duration too short ({record_duration:.1f}s < {self.min_record_duration}s)")
                return "TOO_SHORT"
        
        # 收集所有音频数据
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        
        if not audio_data:
            logger.warning("没有收集到音频数据")
            return None
            
        # Merge audio data
        audio = np.concatenate(audio_data)
        logger.info(f"Audio data length: {len(audio)} samples")

        # Convert numpy array to byte stream
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio, self.sample_rate, format='WAV')
        audio_buffer.seek(0)  # 将缓冲区指针移动到开始位置
        
        return audio_buffer
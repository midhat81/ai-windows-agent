"""
Microphone audio capture module
Captures audio from default microphone with wake word detection
"""
import sounddevice as sd
import numpy as np
import queue
import threading
from typing import Optional, Callable

class MicrophoneCapture:
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 chunk_duration: float = 0.5):
        """
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1 for mono)
            chunk_duration: Duration of each audio chunk in seconds
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = int(sample_rate * chunk_duration)
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None
        
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        # Add audio data to queue
        self.audio_queue.put(indata.copy())
    
    def start_recording(self):
        """Start capturing audio from microphone"""
        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._audio_callback,
            blocksize=self.chunk_size
        )
        self.stream.start()
        print(f"🎤 Recording started (sample rate: {self.sample_rate}Hz)")
    
    def stop_recording(self):
        """Stop audio capture"""
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        print("🛑 Recording stopped")
    
    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get next audio chunk from queue
        
        Args:
            timeout: Maximum time to wait for audio chunk
            
        Returns:
            Audio data as numpy array, or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def record_for_duration(self, duration: float) -> np.ndarray:
        """
        Record audio for a specific duration
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Complete audio recording as numpy array
        """
        print(f"🎙️ Recording for {duration} seconds...")
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished
        return recording.flatten()
    
    def record_until_silence(self, 
                            silence_threshold: float = 0.01,
                            silence_duration: float = 1.5,
                            max_duration: float = 30.0) -> np.ndarray:
        """
        Record audio until silence is detected
        
        Args:
            silence_threshold: RMS threshold for silence detection
            silence_duration: Duration of silence to stop recording
            max_duration: Maximum recording duration
            
        Returns:
            Complete audio recording as numpy array
        """
        print("🎙️ Recording until silence...")
        audio_data = []
        silence_chunks = 0
        chunks_for_silence = int(silence_duration / (self.chunk_size / self.sample_rate))
        max_chunks = int(max_duration / (self.chunk_size / self.sample_rate))
        
        self.start_recording()
        
        chunk_count = 0
        while chunk_count < max_chunks:
            chunk = self.get_audio_chunk()
            if chunk is None:
                continue
                
            audio_data.append(chunk)
            chunk_count += 1
            
            # Check if chunk is silent
            rms = np.sqrt(np.mean(chunk**2))
            if rms < silence_threshold:
                silence_chunks += 1
            else:
                silence_chunks = 0
            
            # Stop if enough silence detected
            if silence_chunks >= chunks_for_silence:
                print("✅ Silence detected, stopping recording")
                break
        
        self.stop_recording()
        
        # Concatenate all chunks
        if audio_data:
            return np.concatenate(audio_data).flatten()
        return np.array([])


if __name__ == "__main__":
    # Test microphone capture
    mic = MicrophoneCapture()
    
    print("\n=== Testing audio capture ===")
    print("Speak now for 3 seconds...")
    audio = mic.record_for_duration(3.0)
    print(f"Captured {len(audio)} samples ({len(audio)/mic.sample_rate:.2f} seconds)")
    
    print("\n=== Testing silence detection ===")
    print("Speak, then pause for 1.5 seconds to stop...")
    audio = mic.record_until_silence()
    print(f"Captured {len(audio)} samples ({len(audio)/mic.sample_rate:.2f} seconds)")
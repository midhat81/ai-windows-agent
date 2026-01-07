"""
Audio preprocessing utilities
Noise reduction, normalization, and VAD (Voice Activity Detection)
"""
import numpy as np
from scipy import signal
import noisereduce as nr

class AudioPreprocessor:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def normalize_audio(self, audio: np.ndarray, target_level: float = 0.3) -> np.ndarray:
        """
        Normalize audio amplitude
        
        Args:
            audio: Input audio array
            target_level: Target peak amplitude (0.0 to 1.0)
            
        Returns:
            Normalized audio
        """
        if len(audio) == 0:
            return audio
        
        # Avoid division by zero
        max_val = np.max(np.abs(audio))
        if max_val == 0:
            return audio
        
        # Normalize to target level
        return audio * (target_level / max_val)
    
    def reduce_noise(self, 
                    audio: np.ndarray, 
                    noise_profile: np.ndarray = None) -> np.ndarray:
        """
        Reduce background noise using spectral gating
        
        Args:
            audio: Input audio array
            noise_profile: Optional noise sample for profiling
            
        Returns:
            Noise-reduced audio
        """
        if len(audio) == 0:
            return audio
        
        # Use noise reduction library
        if noise_profile is not None:
            reduced = nr.reduce_noise(
                y=audio, 
                sr=self.sample_rate,
                y_noise=noise_profile,
                prop_decrease=1.0
            )
        else:
            # Use stationary noise reduction
            reduced = nr.reduce_noise(
                y=audio, 
                sr=self.sample_rate,
                stationary=True
            )
        
        return reduced
    
    def apply_highpass_filter(self, 
                             audio: np.ndarray, 
                             cutoff: int = 80) -> np.ndarray:
        """
        Apply high-pass filter to remove low-frequency noise
        
        Args:
            audio: Input audio array
            cutoff: Cutoff frequency in Hz
            
        Returns:
            Filtered audio
        """
        if len(audio) == 0:
            return audio
        
        # Design high-pass filter
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='high')
        
        # Apply filter
        filtered = signal.filtfilt(b, a, audio)
        return filtered
    
    def detect_voice_activity(self, 
                            audio: np.ndarray,
                            frame_duration: float = 0.02,
                            energy_threshold: float = 0.01) -> np.ndarray:
        """
        Simple Voice Activity Detection based on energy
        
        Args:
            audio: Input audio array
            frame_duration: Duration of each analysis frame
            energy_threshold: Energy threshold for voice detection
            
        Returns:
            Boolean array indicating voice activity per frame
        """
        if len(audio) == 0:
            return np.array([])
        
        frame_size = int(frame_duration * self.sample_rate)
        num_frames = len(audio) // frame_size
        
        vad_result = []
        for i in range(num_frames):
            frame = audio[i * frame_size:(i + 1) * frame_size]
            energy = np.sqrt(np.mean(frame**2))
            vad_result.append(energy > energy_threshold)
        
        return np.array(vad_result)
    
    def trim_silence(self, 
                    audio: np.ndarray,
                    threshold: float = 0.01,
                    frame_duration: float = 0.02) -> np.ndarray:
        """
        Trim leading and trailing silence from audio
        
        Args:
            audio: Input audio array
            threshold: Energy threshold for silence
            frame_duration: Duration of analysis frame
            
        Returns:
            Trimmed audio
        """
        if len(audio) == 0:
            return audio
        
        # Detect voice activity
        vad = self.detect_voice_activity(audio, frame_duration, threshold)
        
        # Find first and last voice frames
        voice_indices = np.where(vad)[0]
        if len(voice_indices) == 0:
            return audio  # No voice detected, return original
        
        frame_size = int(frame_duration * self.sample_rate)
        start_frame = voice_indices[0]
        end_frame = voice_indices[-1] + 1
        
        # Trim audio
        start_sample = start_frame * frame_size
        end_sample = end_frame * frame_size
        
        return audio[start_sample:end_sample]
    
    def preprocess(self, 
                  audio: np.ndarray,
                  apply_noise_reduction: bool = True,
                  apply_normalization: bool = True,
                  apply_trim: bool = True) -> np.ndarray:
        """
        Full preprocessing pipeline
        
        Args:
            audio: Input audio array
            apply_noise_reduction: Whether to apply noise reduction
            apply_normalization: Whether to normalize amplitude
            apply_trim: Whether to trim silence
            
        Returns:
            Preprocessed audio
        """
        processed = audio.copy()
        
        # Apply high-pass filter
        processed = self.apply_highpass_filter(processed)
        
        # Reduce noise
        if apply_noise_reduction:
            processed = self.reduce_noise(processed)
        
        # Trim silence
        if apply_trim:
            processed = self.trim_silence(processed)
        
        # Normalize
        if apply_normalization:
            processed = self.normalize_audio(processed)
        
        return processed


if __name__ == "__main__":
    # Test preprocessing
    preprocessor = AudioPreprocessor()
    
    # Generate test signal with noise
    duration = 2.0
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Clean signal (sine wave)
    clean_signal = np.sin(2 * np.pi * 440 * t)
    
    # Add noise
    noise = np.random.normal(0, 0.1, len(clean_signal))
    noisy_signal = clean_signal + noise
    
    # Preprocess
    processed = preprocessor.preprocess(noisy_signal)
    
    print(f"Original signal length: {len(noisy_signal)}")
    print(f"Processed signal length: {len(processed)}")
    print(f"Noise reduction: {np.mean(np.abs(noisy_signal - clean_signal)):.4f} -> {np.mean(np.abs(processed - clean_signal)):.4f}")
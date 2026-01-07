"""
Faster-Whisper Speech-to-Text integration
Offline, efficient speech recognition
"""
from faster_whisper import WhisperModel
import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class TranscriptionSegment:
    """Single transcription segment with timing"""
    text: str
    start: float
    end: float
    confidence: float

class FasterWhisperSTT:
    def __init__(self, 
                 model_size: str = "base",
                 device: str = "cpu",
                 compute_type: str = "int8"):
        """
        Initialize Faster-Whisper model
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v2)
            device: Device to use (cpu, cuda)
            compute_type: Computation precision (int8, float16, float32)
        """
        print(f"🔄 Loading Faster-Whisper model: {model_size}")
        self.model = WhisperModel(
            model_size, 
            device=device, 
            compute_type=compute_type
        )
        print(f"✅ Model loaded: {model_size} on {device}")
        
    def transcribe(self, 
                  audio: np.ndarray,
                  language: str = "en",
                  task: str = "transcribe",
                  vad_filter: bool = True) -> Tuple[str, List[TranscriptionSegment]]:
        """
        Transcribe audio to text
        
        Args:
            audio: Audio array (float32, normalized to [-1, 1])
            language: Target language code
            task: 'transcribe' or 'translate'
            vad_filter: Apply Voice Activity Detection filter
            
        Returns:
            Full transcription text and list of segments
        """
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # Transcribe with Faster-Whisper
        segments, info = self.model.transcribe(
            audio,
            language=language,
            task=task,
            vad_filter=vad_filter,
            beam_size=5
        )
        
        # Collect segments
        transcription_segments = []
        full_text = []
        
        for segment in segments:
            seg = TranscriptionSegment(
                text=segment.text.strip(),
                start=segment.start,
                end=segment.end,
                confidence=segment.avg_logprob
            )
            transcription_segments.append(seg)
            full_text.append(seg.text)
        
        # Combine all text
        complete_text = " ".join(full_text)
        
        print(f"🎯 Transcribed: {complete_text}")
        return complete_text, transcription_segments
    
    def detect_wake_word(self, 
                        audio: np.ndarray,
                        wake_words: List[str] = ["hey computer", "computer"]) -> bool:
        """
        Check if audio contains wake word
        
        Args:
            audio: Audio array
            wake_words: List of acceptable wake words/phrases
            
        Returns:
            True if wake word detected
        """
        text, _ = self.transcribe(audio)
        text_lower = text.lower().strip()
        
        for wake_word in wake_words:
            if wake_word.lower() in text_lower:
                print(f"✅ Wake word detected: '{wake_word}'")
                return True
        
        return False
    
    def transcribe_streaming(self, 
                           audio_chunks: List[np.ndarray],
                           language: str = "en") -> str:
        """
        Transcribe streaming audio chunks
        (Note: Faster-Whisper doesn't support true streaming,
         this concatenates chunks for batch processing)
        
        Args:
            audio_chunks: List of audio chunk arrays
            language: Target language
            
        Returns:
            Complete transcription
        """
        # Concatenate all chunks
        full_audio = np.concatenate(audio_chunks)
        
        # Transcribe complete audio
        text, _ = self.transcribe(full_audio, language=language)
        return text


if __name__ == "__main__":
    # Test STT
    print("=== Testing Faster-Whisper STT ===\n")
    
    # Initialize STT
    stt = FasterWhisperSTT(model_size="base")
    
    # Test with microphone input
    from audio.mic_input import MicrophoneCapture
    from audio.preprocess import AudioPreprocessor
    
    mic = MicrophoneCapture()
    preprocessor = AudioPreprocessor()
    
    print("\n📢 Say something (3 seconds)...")
    audio = mic.record_for_duration(3.0)
    
    # Preprocess
    audio = preprocessor.preprocess(audio)
    
    # Transcribe
    text, segments = stt.transcribe(audio)
    
    print(f"\n✅ Full transcription: {text}")
    print(f"\n📋 Segments:")
    for seg in segments:
        print(f"  [{seg.start:.2f}s - {seg.end:.2f}s] {seg.text}")
    
    # Test wake word
    print("\n\n=== Testing Wake Word Detection ===")
    print("📢 Say 'hey computer' or 'computer' (3 seconds)...")
    audio = mic.record_for_duration(3.0)
    audio = preprocessor.preprocess(audio)
    
    detected = stt.detect_wake_word(audio)
    if detected:
        print("✅ Wake word detected!")
    else:
        print("❌ No wake word detected")
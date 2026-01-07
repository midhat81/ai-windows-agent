"""
AI Windows Voice Agent - Main Entry Point (Day 1)
Audio Capture + Speech-to-Text Testing
"""
import json
from audio.mic_input import MicrophoneCapture
from audio.preprocess import AudioPreprocessor
from stt.faster_whisper_stt import FasterWhisperSTT

class VoiceAgent:
    def __init__(self, config_path: str = "config.json"):
        """Initialize voice agent with config"""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize components
        print("🚀 Initializing AI Voice Agent...")
        
        self.mic = MicrophoneCapture(
            sample_rate=self.config['audio']['sample_rate']
        )
        
        self.preprocessor = AudioPreprocessor(
            sample_rate=self.config['audio']['sample_rate']
        )
        
        self.stt = FasterWhisperSTT(
            model_size=self.config['stt']['model_size'],
            device=self.config['stt']['device']
        )
        
        self.wake_words = self.config['wake_words']
        
        print("✅ Voice agent initialized\n")
    
    def listen_for_wake_word(self) -> bool:
        """
        Listen for wake word activation
        
        Returns:
            True if wake word detected
        """
        print("👂 Listening for wake word...")
        print(f"   Say one of: {', '.join(self.wake_words)}\n")
        
        # Record short audio clip
        audio = self.mic.record_for_duration(3.0)
        
        # Preprocess
        audio = self.preprocessor.preprocess(
            audio,
            apply_noise_reduction=True,
            apply_normalization=True
        )
        
        # Check for wake word
        detected = self.stt.detect_wake_word(audio, self.wake_words)
        
        return detected
    
    def listen_for_command(self) -> str:
        """
        Record and transcribe user command
        
        Returns:
            Transcribed command text
        """
        print("\n🎤 Listening for your command...")
        print("   (Speak, then pause for 1.5 seconds)\n")
        
        # Record until silence
        audio = self.mic.record_until_silence(
            silence_duration=1.5,
            max_duration=15.0
        )
        
        # Preprocess
        audio = self.preprocessor.preprocess(audio)
        
        # Transcribe
        text, segments = self.stt.transcribe(audio)
        
        return text
    
    def run_test_mode(self):
        """
        Day 1 test mode: Wake word detection + command transcription
        """
        print("=" * 60)
        print("  AI VOICE AGENT - DAY 1 TEST MODE")
        print("=" * 60)
        print()
        
        while True:
            # Wait for wake word
            if self.listen_for_wake_word():
                print("✅ Wake word detected!\n")
                
                # Get command
                command = self.listen_for_command()
                
                print(f"\n📝 Transcribed command:")
                print(f"   '{command}'")
                print()
                
                # Ask if user wants to continue
                response = input("Continue? (y/n): ").strip().lower()
                if response != 'y':
                    break
            else:
                print("❌ No wake word detected, try again\n")


def main():
    """Main entry point"""
    try:
        agent = VoiceAgent()
        agent.run_test_mode()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
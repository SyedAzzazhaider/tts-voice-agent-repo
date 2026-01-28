"""
Module 5: TTS Engine (Integrated from Team Member)
Converts text to speech with online/offline support
"""

from dataclasses import dataclass
from typing import Optional
import pyttsx3
from gtts import gTTS
import os
import platform
import subprocess
from pathlib import Path
from loguru import logger
from datetime import datetime

@dataclass
class TTSResult:
    """TTS Generation Result"""
    success: bool
    audio_path: str
    language: str
    mode: str  # 'online' or 'offline'
    error: Optional[str] = None

class TTSEngine:
    """Text-to-Speech Engine"""
    
    def __init__(self, output_dir: str = "assets"):
        """Initialize TTS Engine - saves directly to assets/ folder"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"TTS Engine initialized. Output: {self.output_dir.absolute()}")
    
    def generate_speech(self, text: str, language: str = "en") -> TTSResult:
        """
        Generate speech from text
        
        Args:
            text: Input text
            language: 'en' or 'ur'
        
        Returns:
            TTSResult with audio file path
        """
        try:
            if language == "en":
                return self._speak_offline(text)
            else:  # Urdu
                return self._speak_urdu_online(text)
        
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return TTSResult(
                success=False,
                audio_path="",
                language=language,
                mode="",
                error=str(e)
            )
    
    def _speak_offline(self, text: str) -> TTSResult:
        """English offline TTS using pyttsx3"""
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = self.output_dir / f"audio_en_{timestamp}.wav"
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.save_to_file(text, str(audio_path))
            engine.runAndWait()
            
            # Verify file was created
            if not audio_path.exists():
                raise Exception("Audio file not created")
            
            logger.info(f"English TTS saved: {audio_path.absolute()}")
            return TTSResult(
                success=True,
                audio_path=str(audio_path.absolute()),
                language="en",
                mode="offline"
            )
        
        except Exception as e:
            logger.error(f"Offline TTS failed: {e}")
            return TTSResult(
                success=False,
                audio_path="",
                language="en",
                mode="offline",
                error=str(e)
            )
    
    def _speak_urdu_online(self, text: str) -> TTSResult:
        """Urdu online TTS using gTTS"""
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = self.output_dir / f"audio_ur_{timestamp}.mp3"
            
            tts = gTTS(text=text, lang='ur')
            tts.save(str(audio_path))
            
            # Verify file was created
            if not audio_path.exists():
                raise Exception("Audio file not created")
            
            logger.info(f"Urdu TTS saved: {audio_path.absolute()}")
            return TTSResult(
                success=True,
                audio_path=str(audio_path.absolute()),
                language="ur",
                mode="online"
            )
        
        except Exception as e:
            logger.error(f"Online TTS failed: {e}")
            return TTSResult(
                success=False,
                audio_path="",
                language="ur",
                mode="online",
                error=str(e)
            )
    
    def play_audio(self, audio_path: str):
        """Play generated audio file"""
        audio_file = Path(audio_path)
        
        # Check if file exists
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_path}")
            print(f"❌ File not found: {audio_path}")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(str(audio_file))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['afplay', str(audio_file)], check=True)
            else:  # Linux
                subprocess.run(['mpg123', str(audio_file)], check=True)
            
            logger.info(f"Playing audio: {audio_file}")
        
        except Exception as e:
            logger.error(f"Playback failed: {e}")
            print(f"❌ Could not play audio: {e}")


# Convenience function
def generate_speech(text: str, language: str = "en") -> TTSResult:
    """Quick TTS generation"""
    engine = TTSEngine()
    return engine.generate_speech(text, language)
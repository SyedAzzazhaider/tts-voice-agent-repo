import asyncio
import edge_tts
import os
import abc

# Abstract base class for TTS backends
class TTSBackend(abc.ABC):
    @abc.abstractmethod
    async def generate(self, text, voice, rate, output_path):
        pass

class EdgeTTSBackend(TTSBackend):
    async def generate(self, text, voice, rate, output_path):
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)

class OpenAITTSBackend(TTSBackend):
    def __init__(self, api_key=None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    async def generate(self, text, voice, rate, output_path):
        # Note: rate is handled differently or ignored for OpenAI standard TTS
        response = self.client.audio.speech.create(
            model="tts-1-hd", # High definition for human-like quality
            voice=voice or "alloy",
            input=text
        )
        response.stream_to_file(output_path)

class ElevenLabsBackend(TTSBackend):
    def __init__(self, api_key=None):
        from elevenlabs.client import ElevenLabs
        self.client = ElevenLabs(api_key=api_key or os.getenv("ELEVEN_API_KEY"))

    async def generate(self, text, voice, rate, output_path):
        audio = self.client.generate(
            text=text,
            voice=voice or "Rachel",
            model="eleven_multilingual_v2"
        )
        # Handle generator output from ElevenLabs
        with open(output_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

class XTTSBackend(TTSBackend):
    def __init__(self):
        from TTS.api import TTS
        # This will download the model on first run (~1.5GB)
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

    async def generate(self, text, voice, rate, output_path):
        # For XTTS, voice is usually a path to a reference wav for cloning
        # or a speaker name from the model's supported list.
        self.tts.tts_to_file(text=text, speaker=voice or "Ana Helena Tanios", language="en", file_path=output_path)

class TTSEngine:
    def __init__(self, backend_type="edge"):
        self.output_dir = "output_audio"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.backend_type = backend_type.lower()
        self.backend = self.get_backend(self.backend_type)
        
        # Default voices mapping for Edge TTS
        self.edge_voices = {
            "english": "en-US-AriaNeural",
            "urdu": "ur-PK-AsadNeural"
        }

    def get_backend(self, backend_type):
        if backend_type == "openai":
            return OpenAITTSBackend()
        elif backend_type == "elevenlabs":
            return ElevenLabsBackend()
        elif backend_type == "xtts":
            return XTTSBackend()
        else:
            return EdgeTTSBackend()

    async def generate_speech(self, text, language="english", rate="+0%", filename="output.mp3", voice=None):
        """
        Generates speech using the selected backend.
        """
        output_path = os.path.join(self.output_dir, filename)
        
        # Determine voice based on language or provided voice name
        if not voice and self.backend_type == "edge":
            voice = self.edge_voices.get(language.lower(), self.edge_voices["english"])
        
        await self.backend.generate(text, voice, rate, output_path)
        return output_path

    def play_audio(self, file_path):
        """Plays the audio file. Optional: install 'playsound' for CLI playback."""
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return
        try:
            from playsound import playsound
            print(f"Playing: {file_path}")
            playsound(file_path)
        except ImportError:
            print(f"Audio saved: {file_path} (install 'playsound' for playback)")

async def main():
    # Example using Edge TTS (Current)
    tts = TTSEngine(backend_type="edge")
    print("Generating Edge TTS speech...")
    en_file = await tts.generate_speech("Testing the legacy edge engine.", language="english")
    tts.play_audio(en_file)
    
    # Note: XTTS, OpenAI, and ElevenLabs would require API keys or downloading large models.
    # We provide them as options for the user.

if __name__ == "__main__":
    asyncio.run(main())

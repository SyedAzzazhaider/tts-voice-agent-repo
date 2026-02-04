import asyncio
import edge_tts
import os
import abc
import unidecode

# Abstract base class for TTS backends
class TTSBackend(abc.ABC):
    @abc.abstractmethod
    async def generate(self, text, voice, rate, output_path):
        pass

class EdgeTTSBackend(TTSBackend):
    async def generate(self, text, voice, rate, output_path):
        # Edge TTS expects rate string like "+10%" or "-10%"
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)

class Pyttsx3Backend(TTSBackend):
    def __init__(self):
        import pyttsx3
        # SINGLETON FIX: Only initialize pyttsx3 once per process
        if not hasattr(Pyttsx3Backend, '_engine_instance'):
             try:
                Pyttsx3Backend._engine_instance = pyttsx3.init()
                Pyttsx3Backend._engine_instance.setProperty('rate', 150)
             except Exception as e:
                print(f"Failed to init pyttsx3: {e}")
                Pyttsx3Backend._engine_instance = None
        
        self.engine = Pyttsx3Backend._engine_instance
    
    async def generate(self, text, voice, rate, output_path):
        # pyttsx3 handles rate as integer (words per minute), e.g. 150.
        
        # TRANSILITERATION LOGIC FOR OFFLINE URDU
        # Check if text contains non-ASCII characters (likely Urdu/Arabic)
        if any(ord(c) > 127 for c in text):
            # SAFE PRINT: Encode to avoid charmap errors on Windows
            safe_text = text[:20].encode('ascii', 'replace').decode('ascii')
            print(f"[WARN] Non-English text detected in offline mode: {safe_text}...")
            print("[INFO] Transliterating to Roman Urdu for basic playback...")
            try:
                # Custom simple mapping for better vowel retention
                mapping = {
                    'ا': 'a', 'آ': 'aa', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 't', 'ث': 's',
                    'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ڈ': 'd', 'ذ': 'z',
                    'ر': 'r', 'ڑ': 'r', 'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
                    'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
                    'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm', 'ن': 'n', 'و': 'o', 'ہ': 'h',
                    'ی': 'i', 'ے': 'ay', 'ھ': 'h', 'ء': "'", 'ں': 'n',
                    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
                    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9', '؟': '?'
                }
                
                roman_text = ""
                for char in text:
                    if char in mapping:
                        roman_text += mapping[char]
                    else:
                        roman_text += char
                
                # Use unidecode as a final cleanup for any missed chars, but our mapping handles main ones
                text = unidecode.unidecode(roman_text)
                
                # Add spaces between words if they were stuck together (simple heuristic)
                # Not perfect but better than nothing
                
                safe_trans = text[:50].encode('ascii', 'replace').decode('ascii')
                print(f"[INFO] Transliterated: {safe_trans}...")
            except Exception as e:
                print(f"[ERROR] Transliteration failed: {e}")

        # Ensure output directory exists (pyttsx3 might not create it)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if os.path.exists(output_path):
            os.remove(output_path)

        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()

class MMSBackend(TTSBackend):
    def __init__(self, language="urdu"):
        try:
            from transformers import VitsModel, AutoTokenizer
            import torch
            import scipy.io.wavfile
            import numpy as np
            
            self.scipy_write = scipy.io.wavfile.write
            # Check for GPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[INFO] MMS-TTS ({language}) initializing on {self.device}...")
            
            # Load model - will download on first run (~50MB - 100MB)
            if language == "english":
                self.model_id = "facebook/mms-tts-eng"
            else:
                self.model_id = "facebook/mms-tts-urd-script_arabic"

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = VitsModel.from_pretrained(self.model_id).to(self.device)
            
            # ⚡ OPTIMIZATION: Apply Dynamic Quantization for CPU Speedup (1.5x - 2x faster)
            if self.device == "cpu":
                print(f"[INFO] Applying Quantization to MMS Model ({language})...")
                self.model = torch.quantization.quantize_dynamic(
                    self.model, {torch.nn.Linear}, dtype=torch.qint8
                )
                
            print(f"[SUCCESS] MMS-TTS ({language}) loaded successfully.")
            
        except ImportError as e:
            print(f"[ERROR] MMS-TTS dependencies missing: {e}")
            raise e
        except Exception as e:
            print(f"[ERROR] Failed to load MMS model ({language}): {e}")
            raise e

    async def generate(self, text, voice, rate, output_path):
        import torch
        
        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = inputs.to(self.device)

        with torch.no_grad():
            output = self.model(**inputs).waveform
        
        # Convert to numpy and save
        waveform = output.cpu().numpy().squeeze()
        
        # Ensure output dir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as WAV (MMS is 16kHz usually)
        # Note: transformers VITS config usually has sampling_rate
        rate = self.model.config.sampling_rate
        
        # If output_path is .mp3, we might need ffmpeg or just save as wav and rename (player might handle it)
        # Ideally, we save as .wav for quality.
        if output_path.endswith(".mp3"):
            output_path = output_path.replace(".mp3", ".wav")
            
        self.scipy_write(output_path, rate, waveform)
        return output_path


class OpenAITTSBackend(TTSBackend):
    def __init__(self, api_key=None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    async def generate(self, text, voice, rate, output_path):
        response = self.client.audio.speech.create(
            model="tts-1-hd",
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
        with open(output_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

class XTTSBackend(TTSBackend):
    def __init__(self):
        from TTS.api import TTS
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

    async def generate(self, text, voice, rate, output_path):
        self.tts.tts_to_file(text=text, speaker=voice or "Ana Helena Tanios", language="en", file_path=output_path)

class TTSEngine:
    def __init__(self, backend_type="edge"):
        self.output_dir = "assets"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.backend_type = backend_type.lower()
        
        # Initialize primary backend
        try:
            self.backend = self.get_backend(self.backend_type)
        except Exception as e:
            print(f"[WARN] Primary backend {self.backend_type} failed: {e}. Falling back to pyttsx3")
            self.backend = Pyttsx3Backend()
        
        # Pre-load Neural Backend for offline Urdu/English (lazy load)
        self.neural_urdu_backend = None
        self.neural_english_backend = None

        self.edge_voices = {
            "english": "en-US-AriaNeural",
            "urdu": "ur-PK-AsadNeural"
        }

    def get_backend(self, backend_type):
        if backend_type == "pyttsx3" or backend_type == "offline":
            return Pyttsx3Backend()
        elif backend_type == "mms" or backend_type == "neural":
             return MMSBackend()
        elif backend_type == "openai":
            return OpenAITTSBackend()
        elif backend_type == "elevenlabs":
            return ElevenLabsBackend()
        elif backend_type == "xtts":
            return XTTSBackend()
        else:
            return EdgeTTSBackend()

    async def generate_speech(self, text, language="english", rate="+0%", filename="output.mp3", voice=None):
        """Generates speech - tries online, falls back to offline human-like (MMS), then offline robotic (pyttsx3)"""
        import time
        import socket
        start_t = time.time()
        
        output_path = os.path.join(self.output_dir, filename)
        
        if not voice and self.backend_type == "edge":
            voice = self.edge_voices.get(language.lower(), self.edge_voices["english"])
        
        # ⚡ OPTIMIZATION: Robust Internet Check (Try Google then Cloudflare)
        can_use_online = False
        if self.backend_type == "edge":
            try:
                # Primary Check
                socket.create_connection(("www.google.com", 80), timeout=1.5)
                can_use_online = True
            except OSError:
                try:
                    # Backup Check (Cloudflare DNS)
                    socket.create_connection(("1.1.1.1", 53), timeout=1.5)
                    can_use_online = True
                except OSError:
                    print("[WARN] No Internet detected (Double Check Failed). Skipping Online TTS.")
                    can_use_online = False
        
        # ---------------------------------------------------------
        # TIER 1: Online (Edge TTS) - Best Quality
        # ---------------------------------------------------------
        try:
            if can_use_online:
                print(f"[INFO] [TIER 1] Starting Online TTS ({self.backend_type})...")
                await self.backend.generate(text, voice, rate, output_path)
                
                # Verify file
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print(f"[INFO] TTS Generation took {time.time() - start_t:.2f}s")
                    return output_path
                else:
                    raise Exception("Generated audio file is empty")
            else:
                 print("[WARN] Skipping Tier 1 (Offline Mode)")
                 
        except Exception as e:
            print(f"[WARN] [TIER 1] Online TTS failed: {e}")

        # ---------------------------------------------------------
        # TIER 2: Offline Human-Like (MMS Neural) - High Quality
        # ---------------------------------------------------------
        print("[INFO] [TIER 2] Attempting Neural Offline TTS (MMS)...")
        
        wav_path = output_path.replace(".mp3", ".wav") # MMS outputs WAV
        
        try:
            is_urdu = any(ord(c) > 127 for c in text) or "urdu" in language.lower()
            target_lang = "urdu" if is_urdu else "english"
            
            # Lazy Load the correct backend
            backend_attr = f"neural_{target_lang}_backend"
            current_backend = getattr(self, backend_attr)
            
            if not current_backend:
                print(f"[INFO] Initializing {target_lang} Neural Model (First Run)...")
                init_t = time.time()
                current_backend = MMSBackend(language=target_lang)
                setattr(self, backend_attr, current_backend)
                print(f"[INFO] Neural Init took {time.time() - init_t:.2f}s")
            
            gen_t = time.time()
            await current_backend.generate(text, None, rate, wav_path)
            print(f"[INFO] Neural Generate took {time.time() - gen_t:.2f}s")
            
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                return wav_path
            else:
                raise Exception("Neural output empty")

        except Exception as neur_e:
            print(f"[ERROR] [TIER 2] Neural Offline failed: {neur_e}")

        # ---------------------------------------------------------
        # TIER 3: Offline Backup (pyttsx3) - Robotic but Reliable
        # ---------------------------------------------------------
        print("[WARN] [TIER 3] Switching to System Fallback (pyttsx3)...")
        try:
            offline_backend = Pyttsx3Backend()
            await offline_backend.generate(text, None, rate, output_path)
            print(f"[INFO] Backup Generate took {time.time() - start_t:.2f}s")
            return output_path
        except Exception as ev:
            print(f"[ERROR] [TIER 3] All TTS methods failed: {ev}")
            raise ev

    def play_audio(self, file_path):
        """Plays the audio file"""
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return
        
        # Simple playback check (optional)
        print(f"Audio ready at: {file_path}")

async def main():
    tts = TTSEngine(backend_type="edge")
    print("Generating speech...")
    en_file = await tts.generate_speech("Testing offline fallback.", language="english")
    print(f"File generated: {en_file}")

if __name__ == "__main__":
    asyncio.run(main())

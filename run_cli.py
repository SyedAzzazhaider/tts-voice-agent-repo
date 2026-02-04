"""
Main Application - TTS Voice Agent (Integrated System)
Combines all team modules into one pipeline
"""

from config import startup, settings
from modules.text_input import process_text
from modules.file_extractor import extract_text as extract_from_file
from modules.ocr_engine import extract_text_from_image
from modules.language_detector import quick_detect
from modules.tts_engine import TTSEngine

def main():
    """
    Main pipeline: Input → Extract → Detect Language → Generate Speech
    """
    
    # Initialize system
    logger = startup()
    tts = TTSEngine()
    
    logger.info("=" * 60)
    logger.success("✅ TTS VOICE AGENT - ALL MODULES INTEGRATED")
    logger.info("=" * 60)
    
    # Display config
    print(f"\n📊 System Configuration:")
    print(f"   • App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   • Languages: {', '.join(settings.SUPPORTED_LANGUAGES)}")
    print(f"   • Audio Format: {settings.AUDIO_FORMAT.upper()}")
    print(f"   • Max File Size: {settings.MAX_FILE_SIZE_MB}MB")
    
    # User input
    print("\n" + "="*60)
    print("📥 SELECT INPUT TYPE:")
    print("="*60)
    print("\n1. 📝 Direct Text Input")
    print("2. 📄 PDF/DOCX File")
    print("3. 🖼️  Image (Screenshot/Photo)")
    
    choice = input("\nChoose (1-3): ").strip()
    
    # Step 1: Extract Text
    print("\n" + "="*60)
    print("STEP 1: TEXT EXTRACTION")
    print("="*60)
    
    try:
        if choice == "1":
            # Direct text input
            user_text = input("\n📝 Enter text: ")
            result = process_text(user_text)
            
            if not result.success:
                print(f"❌ Error: {result.error}")
                return
            
            text = result.text
            print(f"✅ Text processed ({result.char_count} chars, {result.word_count} words)")
        
        elif choice == "2":
            # File extraction
            file_path = input("\n📄 Enter file path: ")
            result = extract_from_file(file_path)
            
            if not result.success:
                print(f"❌ Error: {result.error}")
                return
            
            text = result.text
            print(f"✅ Extracted from {result.file_type.upper()} ({result.page_count} pages, {result.char_count} chars)")
        
        elif choice == "3":
            # Image OCR
            image_path = input("\n🖼️  Enter image path: ")
            result = extract_text_from_image(image_path)
            
            if not result.success:
                print(f"❌ Error: {result.error}")
                return
            
            text = result.text
            print(f"✅ OCR completed ({result.confidence:.1f}% confidence, {result.char_count} chars)")
        
        else:
            print("❌ Invalid choice!")
            return
    
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return
    
    # Step 2: Language Detection
    print("\n" + "="*60)
    print("STEP 2: LANGUAGE DETECTION")
    print("="*60)
    
    lang = quick_detect(text)
    lang_name = "Urdu (اردو)" if lang == "ur" else "English"
    print(f"✅ Detected: {lang_name}")
    
    # Show preview
    print(f"\n📄 Text Preview:")
    print(f"   {text[:100]}{'...' if len(text) > 100 else ''}")
    
    # Step 3: TTS Generation
    print("\n" + "="*60)
    print("STEP 3: SPEECH GENERATION")
    print("="*60)
    
    print(f"🔊 Generating {lang_name} audio...")
    tts_result = tts.generate_speech(text, lang)
    
    if tts_result.success:
        print(f"✅ Audio generated successfully!")
        print(f"   • File: {tts_result.audio_path}")
        print(f"   • Language: {tts_result.language}")
        print(f"   • Mode: {tts_result.mode}")
        
        # Play audio
        play_choice = input("\n▶️  Play audio now? (y/n): ").strip().lower()
        if play_choice == 'y':
            print("🔊 Playing audio...")
            tts.play_audio(tts_result.audio_path)
    else:
        print(f"❌ TTS failed: {tts_result.error}")
    
    print("\n" + "="*60)
    print("✅ PROCESS COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

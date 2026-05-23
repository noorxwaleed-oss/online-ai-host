from deep_translator import GoogleTranslator

def translate_text(text, target_language="en"):
    try:
        translated = GoogleTranslator(
            source="auto",
            target=target_language
        ).translate(text)
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return text

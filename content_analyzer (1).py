import os
import hashlib
import json
import re
import warnings

from config import MODEL_NAME
from loaders import load_data
from vector_db import get_embedding_func, create_vectorstore
from analyzer import run_smart_analysis, translator
from langchain_chroma import Chroma

warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def main():

    source_input = input("Enter PDF path or URL:  ")
    user_language_choice = input(
        "Enter target language (e.g., Arabic, English): "
    )

    file_name = os.path.basename(source_input)

    folder_suffix = hashlib.md5(
        file_name.encode()
    ).hexdigest()[:8]

    unique_path = f"vectorstore_{folder_suffix}"

    embedding_func = get_embedding_func()

    if not os.path.exists(unique_path):

        print("📄 Loading data...")

        pages = load_data(source_input)

        print("🧠 Creating vectorstore...")

        vectorstore = create_vectorstore(
            pages,
            embedding_func,
            unique_path
        )

    else:

        print("📦 Loading existing vectorstore...")

        vectorstore = Chroma(
            persist_directory=unique_path,
            embedding_function=embedding_func
        )

    try:

        print(
            "🧠 جاري تحليل المحتوى الآن... قد يستغرق ذلك بضع ثوانٍ."
        )

        analysis = run_smart_analysis(vectorstore)

        if not analysis or analysis.strip() == "":
            raise ValueError("النموذج لم يُرجع أي محتوى.")

        analysis = re.sub(
            r"```json|```",
            "",
            analysis
        ).strip()

        json_start = analysis.find("{")

        if json_start != -1:
            analysis = analysis[json_start:]

        analysis_json = json.loads(analysis)

        source_lang = analysis_json.get(
            "source_language",
            "unknown"
        )

        print(f"🌍 لغة المحتوى الأصلية: {source_lang}")

        if source_lang.lower() != user_language_choice.lower():

            print(
                f"🔄 جاري ترجمة التحليل إلى "
                f"{user_language_choice}..."
            )

            translated_analysis = translator(
                analysis_json,
                target_lang=user_language_choice
            )

            translated_analysis = re.sub(
                r"```json|```",
                "",
                translated_analysis
            ).strip()

            json_start = translated_analysis.find("{")

            if json_start != -1:
                translated_analysis = translated_analysis[json_start:]

            final_analysis = json.loads(translated_analysis)

        else:

            print(
                "✅ لا حاجة للترجمة، لغة المحتوى مطابقة "
                "للغة المطلوبة."
            )

            final_analysis = analysis_json

        print(
            f"✅ تم التحليل بنجاح! "
            f"تم استخراج {len(final_analysis['topics'])} موضوعاً."
        )

        print("-" * 40)

        print(
            json.dumps(
                final_analysis,
                indent=2,
                ensure_ascii=False
            )
        )

        print("-" * 40)

    except json.JSONDecodeError as e:

        print("❌ فشل تحويل الناتج إلى JSON صالح.")
        print(f"تفاصيل الخطأ: {e}")

    except Exception as e:

        print(f"❌ حدث خطأ أثناء التحليل: {e}")


if __name__ == "__main__":
    main()
from django.conf import settings
from django.db import models

class EnsureTranslationsMixin:
    def ensure_all_translations(self, fields, base_lang=None):
        langs = [code for code, _ in getattr(settings, "LANGUAGES", [("uk", "Ukrainian")])]
        base_lang = base_lang or getattr(settings, "LANGUAGE_CODE", "uk")

        base_val = {
            f: self.safe_translation_getter(f, language_code=base_lang, any_language=True)
            for f in fields
        }

        for code in langs:
            if not self.has_translation(code):
                self.set_current_language(code)
                for f in fields:
                    setattr(self, f, base_val.get(f) or "")
                models.Model.save(self, update_fields=[])
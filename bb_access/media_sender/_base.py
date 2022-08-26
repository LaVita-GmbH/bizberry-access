import os
from datetime import datetime
from functools import cached_property
import jinja2
from pydantic import BaseModel
from babel import Locale
from babel.dates import format_date, format_datetime
from babel.numbers import format_currency
from langcodes import closest_match, Language
from jsonpath_ng import parse
from django.conf import settings


class Content(BaseModel):
    subject: str
    receiver: str
    template: str
    language: str
    values: dict

    @property
    def _jinja_env(self):
        language = Language(self.language)
        locale = Locale(language.language, language.territory)

        def find_translation(translations):
            use_language, _ = closest_match(language, [translation['language'] for translation in translations], max_distance=1000)

            return next(filter(lambda t: t['language'] == use_language, translations))

        env = jinja2.Environment()
        env.filters['jpath'] = lambda p: parse(p).find(self.values)[0].value
        env.filters['format_date'] = lambda s: format_date(datetime.fromisoformat(s).date(), locale=locale)
        env.filters['format_datetime'] = lambda s: format_datetime(datetime.fromisoformat(s), locale=locale)
        env.filters['format_currency'] = lambda f, currency: format_currency(f, currency, '#,##0.00 ¤', locale=locale)
        env.filters['format_territory'] = lambda s: locale.territories[s]
        env.filters['find_translation'] = find_translation

        return env

    def _template_render(self) -> str:
        with open(os.path.join(settings.BASE_DIR, 'bb_access', 'templates', self.template), 'rb') as template:
            return self._jinja_env.from_string(str(template.read(), 'utf-8')).render(self.values)

    @property
    def body(self) -> str:
        return self._template_render()


class Sender:
    MEDIUM: str
    INTEGRATION: str

    def __init__(self, content: Content):
        self.content = content
        self.is_sent: bool = False

    def send(self):
        raise NotImplementedError

    @classmethod
    def get_sender(cls, medium: str):
        for scls in cls.__subclasses__():
            if scls.MEDIUM != medium:
                continue

            for integration in scls.__subclasses__():
                if integration.INTEGRATION == getattr(settings, f'SENDER_{medium}_INTEGRATION'):
                    return integration

        raise NotImplementedError

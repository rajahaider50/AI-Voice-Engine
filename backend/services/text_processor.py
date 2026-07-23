import re
from typing import List, Tuple
from ..core.config import Language


class TextProcessor:
    def __init__(self):
        self.sentence_enders = re.compile(r'[.!?؟।\n]+')
        self.punctuation = re.compile(r'[^\w\s\u0600-\u06FF\u0900-\u097F\u0980-\u09FF]')

    def clean_text(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:\u0600-\u06FF\u0900-\u097F\u0980-\u09FF]', '', text)
        return text

    def split_sentences(self, text: str, language: Language) -> List[str]:
        if language == Language.URDU:
            sentences = re.split(r'[۔؟!\n]+', text)
        elif language == Language.HINDI:
            sentences = re.split(r'[।?!?\n]+', text)
        else:
            sentences = self.sentence_enders.split(text)

        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def detect_emotion(self, text: str) -> str:
        text_lower = text.lower()

        happy_words = ['happy', 'glad', 'joy', 'wonderful', 'great', 'love', 'excited',
                       'خوش', 'اچھا', 'بہت اچھا', 'شاد', 'خوشی']
        sad_words = ['sad', 'sorry', 'unfortunately', 'miss', 'lost', 'crying',
                     'اداس', 'افسوس', 'دوکھ', 'رو']
        angry_words = ['angry', 'furious', 'hate', 'annoyed', 'stupid',
                       'غصہ', 'ناراض', 'نفرت', 'بےوقوف']
        surprised_words = ['wow', 'amazing', 'incredible', 'surprised', 'unbelievable',
                           'حیران', 'کمال', 'بے شکل']

        for word in happy_words:
            if word in text_lower:
                return "happy"
        for word in sad_words:
            if word in text_lower:
                return "sad"
        for word in angry_words:
            if word in text_lower:
                return "angry"
        for word in surprised_words:
            if word in text_lower:
                return "surprised"

        return "neutral"

    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        words = len(text.split())
        base_duration = words / 2.5
        return base_duration / speed

    def add_pause_markers(self, text: str, pause_length: float = 0.5) -> str:
        if pause_length > 0.3:
            text = re.sub(r'([.!?])', r'\1 <break time="{}s"/>'.format(pause_length), text)
        return text

class InvalidMoodError(Exception):
    """Исключение, вызываемое при неверном настроении."""
    def __init__(self, mood: str):
        super().__init__(f"Извини, я не знаю такого настроения: {mood}. Попробуй еще раз!")
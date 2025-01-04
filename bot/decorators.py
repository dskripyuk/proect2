def validate_mood(func):
    """Декоратор для валидации настроения."""
    def wrapper(self, mood: str):
        if mood not in self.movies_by_mood:
            raise InvalidMoodError(mood)
        return func(self, mood)
    return wrapper
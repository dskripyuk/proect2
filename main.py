from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from movie_recommender import MovieRecommender
from exceptions import InvalidMoodError
import random
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация MovieRecommender
movie_recommender = MovieRecommender()


# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text(
        "Привет! Я бот, который подберет фильм под твое настроение. "
        "Напиши, какое у тебя настроение (грусть, радость, страх, гнев, спокойствие)."
    )


# Обработка сообщений с настроением
async def handle_mood(update: Update, context: CallbackContext) -> None:
    """Обработчик сообщений с настроением."""
    user_mood = update.message.text.lower()
    try:
        # Проверяем, есть ли введённое настроение в списке допустимых
        if user_mood not in movie_recommender.movies_by_mood:
            await update.message.reply_text(
                "Извини, я не знаю такого настроения. Попробуй ещё раз!\n"
                "Доступные настроения: грусть, радость, страх, гнев, спокойствие."
            )
            return

        movies = movie_recommender.get_movies_by_mood(user_mood)
        context.user_data["movies"] = movies.copy()  # Сохраняем копию списка фильмов
        random_movie = random.choice(context.user_data["movies"])  # Выбираем случайный фильм
        context.user_data["movies"].remove(random_movie)  # Удаляем выбранный фильм из списка

        response = f"Вот фильм, который подходит под твое настроение ({user_mood}):\n{random_movie}"

        # Создаем кнопки "Ещё фильм" и "Сброс"
        keyboard = [
            [InlineKeyboardButton("Ещё фильм", callback_data=user_mood)],
            [InlineKeyboardButton("Сброс", callback_data="reset")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем сообщение с кнопками
        await update.message.reply_text(response, reply_markup=reply_markup)

    except InvalidMoodError as e:
        await update.message.reply_text(str(e))


# Обработка нажатия кнопок
async def handle_button(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатия кнопок."""
    query = update.callback_query
    data = query.data  # Получаем данные из callback_data

    if data == "reset":
        # Обработка кнопки "Сброс"
        if "movies" in context.user_data:
            del context.user_data["movies"]  # Очищаем список фильмов
        await query.edit_message_text("Список фильмов сброшен. Напиши своё настроение снова!")
        return

    # Обработка кнопки "Ещё фильм"
    user_mood = data
    try:
        if "movies" not in context.user_data or not context.user_data["movies"]:
            # Если фильмы закончились
            await query.edit_message_text("Фильмы для этого настроения закончились!")
            return

        random_movie = random.choice(context.user_data["movies"])  # Выбираем случайный фильм
        context.user_data["movies"].remove(random_movie)  # Удаляем выбранный фильм из списка

        response = f"Вот ещё один фильм, который подходит под твое настроение ({user_mood}):\n{random_movie}"

        # Создаем кнопки "Ещё фильм" и "Сброс"
        keyboard = [
            [InlineKeyboardButton("Ещё фильм", callback_data=user_mood)],
            [InlineKeyboardButton("Сброс", callback_data="reset")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Редактируем сообщение с новым фильмом и кнопками
        await query.edit_message_text(response, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка в handle_button: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте ещё раз.")


# Основная функция
def main() -> None:
    """Запуск бота."""
    # Вставьте сюда ваш токен
    TOKEN = "8035617472:AAFyyNMoGZHlCJZpoNbknmGvwD_CbozqJLQ"

    # Инициализация бота
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mood))
    application.add_handler(CallbackQueryHandler(handle_button))  # Обработчик кнопок

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
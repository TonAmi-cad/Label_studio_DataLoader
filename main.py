"""Main application module"""
import os
import sys
import locale

# Устанавливаем кодировку для консоли Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from api.label_studio_api import LabelStudioAPI
from processors.directory_processor import DirectoryProcessor
from ui.cli import print_welcome_message, get_label_config
from utils.logging_utils import logger

def main():
    """Main program function"""
    try:
        print_welcome_message()
        
        # Получаем путь к корневой директории
        directory_path = input("Введите путь к директории с папками изображений: ").strip()
        
        if not os.path.isdir(directory_path):
            logger.error("Указанный путь не является директорией")
            return
            
        label_config = get_label_config()
        if not label_config:
            logger.error("Не удалось получить конфигурацию разметки")
            return

        api = LabelStudioAPI()
        processor = DirectoryProcessor(api, label_config)
        
        # Обрабатываем корневую директорию
        processor.process_directory(directory_path)
        
        logger.info("Обработка успешно завершена")
        
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        raise

if __name__ == "__main__":
    main()

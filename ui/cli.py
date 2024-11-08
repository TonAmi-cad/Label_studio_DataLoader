"""Command Line Interface"""
from typing import Optional, List, Tuple
from config.label_configs import LABEL_CONFIGS
from utils.logging_utils import logger

def print_welcome_message() -> None:
    """Display welcome message"""
    print("Welcome to the Label Studio program!")
    print("=" * 80)
    print("""
    Main program functions:
    - Creating new projects in Label Studio
    - Uploading images for labeling
    - Automatic request retries on errors
    - Setting up labeling interface for drone detection
    """)
    print("=" * 80)

def get_label_config() -> Optional[str]:
    """Get labeling configuration from user"""
    print("\nSelect labeling type:")
    print("1. Brush")
    print("2. Rectangle")
    print("3. Polygon")

    config_map = {
        "1": "brush",
        "2": "rectangle", 
        "3": "polygon"
    }

    while True:
        choice = input("Enter the number of selected labeling type (1-3): ")
        if choice in config_map:
            return LABEL_CONFIGS[config_map[choice]]
        print("Invalid choice. Please select a number from 1 to 3.")

def get_directory_info() -> Tuple[str, Optional[List[str]]]:
    """Get directory path and list of specific folders from user"""
    directory_path = input("Enter path to main directory with image folders: ").strip()
    
    folders_input = input('Enter folder names in format "name1, name2, name3" (empty string to process all folders): ').strip()
    
    specific_folders = None
    if folders_input:
        # Remove quotes if present and split by comma
        folders_input = folders_input.strip('"\'')
        specific_folders = [folder.strip() for folder in folders_input.split(',') if folder.strip()]
        logger.info(f"Selected folders for processing: {', '.join(specific_folders)}")
    else:
        logger.info("All folders in directory will be processed")

def get_directory_and_start_index() -> tuple[str, int]:
    """Получить путь к директории и начальный индекс от пользователя"""
    directory_path = input("Введите путь к директории с изображениями: ").strip()
    
    while True:
        try:
            start_index = int(input("Введите индекс, с которого начать обработку (0 для начала): "))
            if start_index < 0:
                print("Индекс должен быть неотрицательным числом")
                continue
            return directory_path, start_index
        except ValueError:
            print("Пожалуйста, введите корректное число")
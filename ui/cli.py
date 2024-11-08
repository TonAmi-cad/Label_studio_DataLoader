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

def display_projects(projects: list) -> None:
    """Отображение списка проектов"""
    print("\nСписок доступных проектов:")
    print("-" * 50)
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['title']} (ID: {project['id']})")
    print("-" * 50)

def get_projects_for_deletion(projects: list) -> list[int]:
    """Получить список проектов для удаления"""
    display_projects(projects)
    
    print("\nВыберите проекты для удаления:")
    print("1. Все проекты")
    print("2. Выбрать конкретные проекты")
    
    choice = input("Ваш выбор (1 или 2): ").strip()
    
    if choice == "1":
        return [p['id'] for p in projects]
    
    while True:
        try:
            indices = input("Введите номера проектов через запятую (например: 1,3,5): ").strip()
            selected = [int(i.strip()) for i in indices.split(",")]
            
            if not all(1 <= i <= len(projects) for i in selected):
                print(f"Пожалуйста, введите числа от 1 до {len(projects)}")
                continue
                
            return [projects[i-1]['id'] for i in selected]
        except ValueError:
            print("Пожалуйста, введите корректные номера проектов")

def get_deletion_params(projects: list) -> tuple[list[int], str, Optional[int]]:
    """Получить параметры для удаления изображений"""
    project_ids = get_projects_for_deletion(projects)
    
    print("\nВыберите режим удаления изображений:")
    print("1. Удалить все изображения")
    print("2. Удалить несколько изображений с начала")
    print("3. Удалить несколько изображений с конца")
    
    mode_map = {
        "1": "all",
        "2": "first_n",
        "3": "last_n"
    }
    
    while True:
        mode = input("Выберите режим (1-3): ").strip()
        if mode not in mode_map:
            print("Неверный выбор. Пожалуйста, выберите число от 1 до 3.")
            continue
            
        count = None
        if mode in ("2", "3"):
            while True:
                try:
                    count = int(input("Введите количество изображений для удаления: "))
                    if count <= 0:
                        print("Количество должно быть положительным числом")
                        continue
                    break
                except ValueError:
                    print("Пожалуйста, введите корректное число")
        
        return project_ids, mode_map[mode], count
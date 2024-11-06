"""Main application module"""
import os
from api.label_studio_api import LabelStudioAPI
from processors.directory_processor import DirectoryProcessor
from ui.cli import print_welcome_message, get_label_config, get_directory_path
from utils.logging_utils import logger

def main():
    """Main program function"""
    try:
        print_welcome_message()
        
        label_config = get_label_config()
        if not label_config:
            logger.error("Failed to get labeling configuration")
            return

        directory_path = get_directory_path()
        if not os.path.isdir(directory_path):
            logger.error("Specified path is not a directory")
            return

        api = LabelStudioAPI()
        processor = DirectoryProcessor(api, label_config)
        processor.process_directory(directory_path)
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()

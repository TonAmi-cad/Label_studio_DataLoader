"""Directory Handler for Images"""
import os
from typing import Optional, List
from api.label_studio_api import LabelStudioAPI
from utils.logging_utils import logger

class DirectoryProcessor:
    """Class for processing directories with images"""
    def __init__(self, api: LabelStudioAPI, label_config: str):
        self.api = api
        self.label_config = label_config

    def process_directory(self, directory_path: str, specific_folders: Optional[List[str]] = None) -> None:
        """
        Process a directory with images
        
        Args:
            directory_path: path to the base directory
            specific_folders: list of specific folders to process (if None, all folders are processed)
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Path {directory_path} is not a directory")
            return

        folders_to_process = self._get_folders_to_process(directory_path, specific_folders)
        
        if not folders_to_process:
            logger.warning("No folders found for processing")
            return
            
        logger.info(f"The following folders will be processed: {', '.join(folders_to_process)}")
        
        for folder_name in folders_to_process:
            folder_path = os.path.join(directory_path, folder_name)
            if not os.path.isdir(folder_path):
                logger.warning(f"Skipping {folder_name}: not a directory")
                continue

            logger.info(f"Processing folder: {folder_name}")
            project_id = self.api.create_project(folder_name, self.label_config)
            self._process_images(folder_path, project_id)

    def _get_folders_to_process(self, directory_path: str, specific_folders: Optional[List[str]] = None) -> List[str]:
        """Get list of folders to process"""
        all_folders = [f for f in os.listdir(directory_path) 
                      if os.path.isdir(os.path.join(directory_path, f))]
        
        if not specific_folders:
            return all_folders
            
        # Check for existence of specified folders
        existing_folders = []
        for folder in specific_folders:
            if folder in all_folders:
                existing_folders.append(folder)
            else:
                logger.warning(f"Folder {folder} not found in {directory_path}")
                
        return existing_folders

    def _process_images(self, folder_path: str, project_id: int) -> None:
        """Process images in folder"""
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue
                
            logger.info(f"Processing file: {filename}")
            self.api.upload_image(project_id, file_path)

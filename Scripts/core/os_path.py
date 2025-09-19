"""
Cross-platform path configuration for the systematic review metadata curation project.

This module detects the operating system and sets up appropriate file paths for:
- Project source files and datasets
- Extracted HTML and BibTeX cache storage  
- Browser downloads directory
- Firefox profile for web scraping automation

The configuration supports both Windows (development) and Linux (server) environments
with different storage locations optimized for each platform's characteristics.
"""

import platform
import os

def display_current_paths():
    """
    Display current path configuration for user reference and debugging.

    This function prints all configured paths with their purposes and current
    status (exists/missing) to help users understand and configure their environment.
    """
    print("Current Path Configuration")
    print("=" * 50)
    print(f"Operating System: {platform.system()}")
    print()

    # Define path descriptions
    path_descriptions = {
        'MAIN_PATH': {
            'description': 'Project root directory (source code and datasets)',
            'purpose': 'Contains Scripts/, Datasets/, Database/ folders',
            'required': True,
            'changeable': True
        },
        'EXTRACTED_PATH': {
            'description': 'Cache storage for extracted HTML/BibTeX files',
            'purpose': 'High-capacity storage for web scraping cache',
            'required': False,
            'changeable': True
        },
        'DOWNLOAD_PATH': {
            'description': 'Browser downloads directory',
            'purpose': 'Temporary downloads during web scraping',
            'required': False,
            'changeable': True
        },
        'FIREFOX_PROFILE_PATH': {
            'description': 'Firefox profile for web scraping automation',
            'purpose': 'Persistent browser state and preferences',
            'required': False,
            'changeable': True
        }
    }

    # Get current values
    current_paths = {
        'MAIN_PATH': globals().get('MAIN_PATH', 'Not defined'),
        'EXTRACTED_PATH': globals().get('EXTRACTED_PATH', 'Not defined'),
        'DOWNLOAD_PATH': globals().get('DOWNLOAD_PATH', 'Not defined'),
        'FIREFOX_PROFILE_PATH': globals().get('FIREFOX_PROFILE_PATH', 'Not defined')
    }

    # Display each path with status
    for path_name, path_value in current_paths.items():
        desc = path_descriptions[path_name]
        exists = os.path.exists(path_value) if path_value != 'Not defined' else False
        status = "EXISTS" if exists else "MISSING" if path_value != 'Not defined' else "NOT DEFINED"

        print(f"{path_name}:")
        print(f"   Path: {path_value}")
        print(f"   Status: {status}")
        print(f"   Purpose: {desc['description']}")
        print(f"   Use: {desc['purpose']}")
        print(f"   Required: {'Yes' if desc['required'] else 'No'}")
        print(f"   User Configurable: {'Yes' if desc['changeable'] else 'No'}")
        print()

    print("Configuration Notes:")
    print("- Update paths in Scripts/core/os_path.py for your environment")
    print("- MAIN_PATH must point to your project root directory")
    print("- EXTRACTED_PATH can be on a different drive for more storage")
    print("- Missing optional paths will disable related features")
    print("- See CLAUDE.md for detailed setup instructions")


print(platform.system())
if platform.system() == "Windows":
    # Windows development environment paths
    MAIN_PATH = "C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées"  # Project root
    EXTRACTED_PATH = "C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées/Database"  # High-capacity storage for extracted files
    DOWNLOAD_PATH = "C:/Users/guill/Downloads"  # Browser download directory
    FIREFOX_PROFILE_PATH = "C:/Users/guill/AppData/Roaming/Mozilla/Firefox/Profiles/4am1ne92.default-release-1609958750563"  # Firefox profile for web scraping
# C:\\Users\\guill\\.cache\\selenium\\geckodriver\\win64\\0.35.0\\geckodriver.exe

elif platform.system() == "Linux":
    # Linux server environment paths
    MAIN_PATH = "/home/ggenois/PycharmProjects/IFT3150-ProjetCurationMetadonnees"  # Project root
    # EXTRACTED_PATH = "/media/ggenois/Samsung USB/Demo"
    EXTRACTED_PATH = "/media/ggenois/Samsung USB/Projet Curation des métadonnées"  # External storage for extracted files
    DOWNLOAD_PATH = "/home/ggenois/Downloads"  # Browser download directory
    FIREFOX_PROFILE_PATH = "/home/ggenois/snap/firefox/common/.mozilla/firefox/er60u9dx.default"  # Firefox profile for web scraping
else:
    raise Exception("Unsupported system")


# Display paths when module is imported (optional - can be commented out)
if __name__ == "__main__":
    display_current_paths()
else:
    # Uncomment the line below to always show paths when importing this module
    # display_current_paths()
    pass

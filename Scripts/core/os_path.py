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

print(platform.system())
if platform.system() == "Windows":
    # Windows development environment paths
    MAIN_PATH = "C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées"  # Project root
    EXTRACTED_PATH = "E:/Projet Curation des métadonnées"  # High-capacity storage for extracted files
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

import platform

print(platform.system())
if platform.system() == "Windows":
    MAIN_PATH = "C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées"
    EXTRACTED_PATH = "D:/Projet Curation des métadonnées"
    DOWNLOAD_PATH = "C:/Users/guill/Downloads"
    FIREFOX_PROFILE_PATH = "C:/Users/guill/AppData/Roaming/Mozilla/Firefox/Profiles/4am1ne92.default-release-1609958750563"
# C:\\Users\\guill\\.cache\\selenium\\geckodriver\\win64\\0.35.0\\geckodriver.exe

elif platform.system() == "Linux":
    MAIN_PATH = "/home/ggenois/PycharmProjects/IFT3150-ProjetCurationMetadonnees"
    EXTRACTED_PATH = "/media/ggenois/Samsung USB/Demo"
    # EXTRACTED_PATH = "/media/ggenois/Samsung USB/Projet Curation des métadonnées"
    DOWNLOAD_PATH = "/home/ggenois/Downloads"
    FIREFOX_PROFILE_PATH = "/home/ggenois/snap/firefox/common/.mozilla/firefox/er60u9dx.default"
else:
    raise Exception("Unsupported system")

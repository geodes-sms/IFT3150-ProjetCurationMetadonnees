import platform

print(platform.system())
if platform.system() == "Windows":
    MAIN_PATH = "C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées"
    EXTRACTED_PATH = "D:/Projet Curation des métadonnées"
    DOWNLOAD_PATH = "C:/Users/guill/Downloads"
    FIREFOX_PROFILE_PATH = "C:/Users/guill/AppData/Roaming/Mozilla/Firefox/Profiles/4am1ne92.default-release-1609958750563"
elif platform.system() == "Linux":
    MAIN_PATH = "/home/guillaume-genois/PycharmProjects/IFT3150-ProjetCurationMetadonnees"
    EXTRACTED_PATH = "/media/guillaume-genois/Samsung USB/Projet Curation des métadonnées"
    DOWNLOAD_PATH = "/home/guillaume-genois/Downloads"
    FIREFOX_PROFILE_PATH = ""
else:
    raise Exception("Unsupported system")

import re

def normalize_title(filename: str) -> str:
    """
    Convert messy filename to clean movie title.
    """

    # remove extensions
    filename = re.sub(r"\.(mkv|mp4|avi|mov)$", "", filename, flags=re.I)

    # replace dots and underscores
    filename = filename.replace(".", " ").replace("_", " ")

    # remove quality tags
    filename = re.sub(r"\b(1080p|720p|480p|BluRay|WEB-DL|x264|x265)\b", "", filename, flags=re.I)

    # remove encoders
    filename = re.sub(r"\b(Film9|PAHE|YIFY|AdiT|Ganool)\b", "", filename, flags=re.I)

    # clean extra spaces
    filename = re.sub(r"\s+", " ", filename).strip()

    return filename
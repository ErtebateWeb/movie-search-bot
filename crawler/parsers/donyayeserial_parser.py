import re
import urllib.parse
from bs4 import BeautifulSoup
from crawler.parsers.base import BaseParser

VIDEO_EXTENSIONS = (".mkv", ".mp4", ".avi", ".webm", ".m4v")

QUALITY_PATTERN = r"(2160p|1080p|720p|480p|360p)"
SOURCE_PATTERN = r"(BluRay|WEBRip|WEB-DL|WEB\.DL|HDRip|DVDRip|BRRip)"
CODEC_PATTERN = r"(x264|x265|10bit|HEVC|AVC)"
GROUP_PATTERN = r"(YIFY|YTS|RARBG|PSA|Pahe|Ganool|MkvCage|ShAaNiG|Tigole|Ozlem|AvaMovie|Unknown|AdiT)"
SUBTYPE_PATTERN = r"(SoftSub|NoSub|Dubbed)"
DOMAIN_PATTERN = r"DonyayeSerial"

KNOWN_JUNK = [
    "1080p", "720p", "480p", "2160p", "360p",
    "BluRay", "WEBRip", "WEB-DL", "WEB.DL", "HDRip", "DVDRip", "BRRip",
    "x264", "x265", "10bit", "HEVC", "AVC",
    "YIFY", "YTS", "RARBG", "PSA", "Pahe", "Ganool",
    "MkvCage", "ShAaNiG", "Tigole", "Ozlem", "AvaMovie", "Unknown", "AdiT",
    "SoftSub", "NoSub", "Dubbed",
    "DonyayeSerial", "Film2Media", "Farsi",
    "Remastered", "Extended", "Director.Cut", "Theatrical",
]


class DonyayeSerialParser(BaseParser):

    def parse(self, url: str, html: str = None):
        url = urllib.parse.unquote(url)

        if not url.lower().endswith(VIDEO_EXTENSIONS):
            return None

        info = self._parse_url_path(url)
        filename_info = self._parse_filename(url, info)

        # Merge without overwriting url_path fields
        for k, v in filename_info.items():
            if v is not None and info.get(k) is None:
                info[k] = v
            elif k not in info or info[k] is None:
                info[k] = v

        if html:
            table_info = self._parse_html_table(url, html)
            if table_info:
                info.update(table_info)

        info["url"] = url

        if not info.get("title") or len(info["title"]) < 2:
            return None

        return info

    def _parse_url_path(self, url: str) -> dict:
        parts = url.rstrip("/").split("/")

        result = {
            "collection": None,
            "year": None,
            "imdb_id": None,
            "sub_type": None,
            "is_series": False,
            "series_name": None,
            "season": None,
            "episode": None,
        }

        for i, part in enumerate(parts):
            if part in ("series", "series2", "series3", "series4"):
                result["is_series"] = True
                if i + 1 < len(parts):
                    result["series_name"] = parts[i + 1]
                result["collection"] = part
                break
            elif part in ("movies", "movie4"):
                result["collection"] = part
                result["is_series"] = False
                break

        if not result["is_series"]:
            for i, part in enumerate(parts):
                if re.match(r"^(19|20)\d{2}$", part):
                    result["year"] = part
                    if i + 1 < len(parts):
                        imdb = parts[i + 1]
                        if re.match(r"^tt\d+$", imdb):
                            result["imdb_id"] = imdb
                            if i + 2 < len(parts):
                                sub = parts[i + 2]
                                if sub in ("SoftSub", "NoSub", "Dubbed"):
                                    result["sub_type"] = sub
                    break

        else:
            for part in parts:
                season_match = re.match(r"^S(\d+)$", part, re.I)
                if season_match:
                    result["season"] = season_match.group(1)

                ep_match = re.match(r".*[Ss](\d+)[Ee](\d+)", part)
                if ep_match:
                    result["season"] = ep_match.group(1)
                    result["episode"] = ep_match.group(2)

            for part in parts:
                if part in ("SoftSub", "NoSub", "Dubbed"):
                    result["sub_type"] = part
                    break

        return result

    def _parse_filename(self, url: str, url_info: dict = None) -> dict:
        filename = url.rstrip("/").split("/")[-1]

        filename_no_ext = re.sub(
            r"\.(mkv|mp4|avi|webm|m4v)$", "", filename, flags=re.I
        )

        result = {
            "title": None,
            "raw_filename": filename_no_ext,
            "quality": None,
            "source": None,
            "codec": None,
            "group": None,
            "file_size_str": None,
        }

        is_series = url_info.get("is_series", False) if url_info else False
        series_name = url_info.get("series_name") if url_info else None

        quality_match = re.search(QUALITY_PATTERN, filename_no_ext, re.I)
        if quality_match:
            result["quality"] = quality_match.group(1).upper()

        source_match = re.search(SOURCE_PATTERN, filename_no_ext, re.I)
        if source_match:
            result["source"] = source_match.group(1)

        codec_match = re.search(CODEC_PATTERN, filename_no_ext, re.I)
        if codec_match:
            result["codec"] = codec_match.group(1)

        group_match = re.search(GROUP_PATTERN, filename_no_ext, re.I)
        if group_match:
            result["group"] = group_match.group(1)

        title = filename_no_ext

        for junk in KNOWN_JUNK:
            title = re.sub(re.escape(junk), "", title, flags=re.I)

        # Remove year from title (already stored separately)
        year_val = result.get("year", url_info.get("year") if url_info else None)
        if year_val and title.endswith(year_val):
            title = title[: -len(year_val)]
        else:
            title = re.sub(r"\b(19|20)\d{2}\b", "", title)

        # For series, clean up episode noise from title
        if is_series and series_name:
            series_clean = re.sub(r"[._\-]+", " ", series_name)
            if series_clean.lower() in title.lower():
                title = series_clean
            else:
                title = re.sub(r"[Ss]\d+[Ee]\d+", "", title, flags=re.I)
                title = re.sub(r"\d{3,4}p", "", title, flags=re.I)

        title = re.sub(r"[._\-%20]+", " ", title).strip()
        title = re.sub(r"\s+", " ", title).strip()

        result["title"] = title if len(title) >= 2 else None

        return result

    def _parse_html_table(self, url: str, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="table")
        if not table:
            return {}

        filename = url.rstrip("/").split("/")[-1]

        for row in table.find_all("tr"):
            name_cell = row.find("td", class_="n")
            if not name_cell:
                continue

            link = name_cell.find("a")
            if not link:
                continue

            href = link.get("href", "")
            if href.rstrip("/").split("/")[-1] == filename:
                size_cell = row.find("td", class_="s")
                date_cell = row.find("td", class_="m")

                result = {}
                if size_cell:
                    size_text = size_cell.get_text(strip=True)
                    if size_text and size_text != "-":
                        result["file_size_str"] = size_text

                if date_cell:
                    date_text = date_cell.get_text(strip=True)
                    if date_text:
                        result["last_modified"] = date_text

                return result

        return {}


class DonyayeSerialArchiveParser(BaseParser):

    def parse(self, url: str, html: str = None):
        if not html:
            return None

        return self._parse_archive_page(url, html)

    def _parse_archive_page(self, url: str, html: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        movies = []

        sections = soup.find_all("hr")
        for hr in sections:
            movie_block = self._extract_movie_after_hr(hr)
            if movie_block:
                movies.append(movie_block)

        if not movies:
            for h3 in soup.find_all("h3"):
                movie = self._parse_movie_section(h3)
                if movie:
                    movies.append(movie)

        return movies

    def _extract_movie_after_hr(self, hr):
        movie = {}
        current = hr.next_sibling
        current_subtype = None

        while current and current.name != "hr":
            if current.name == "h3":
                text = current.get_text(strip=True)
                match = re.match(r"^\d+\.\s*(.+?)\s*start_year$", text)
                if match:
                    movie["title"] = match.group(1).strip()

            elif current.name == "p":
                text = current.get_text(strip=True)

                imdb_match = re.search(r"IMDb Code:\s*(tt\d+)", text)
                if imdb_match:
                    movie["imdb_id"] = imdb_match.group(1)

                votes_match = re.search(r"IMDb Votes:\s*([\d,]+)", text)
                if votes_match:
                    movie["votes"] = votes_match.group(1).replace(",", "")

                rate_match = re.search(r"IMDb Rates:\s*([\d.]+)", text)
                if rate_match:
                    movie["rating"] = rate_match.group(1)

                # Detect sub-type marker
                bold_tag = current.find("b")
                has_link = current.find("a", href=True) is not None
                if bold_tag and not has_link:
                    bold_text = bold_tag.get_text(strip=True)
                    if bold_text in ("SoftSub", "NoSub", "Dubbed"):
                        current_subtype = bold_text

                # Extract version link
                link = current.find("a", href=True)
                if link:
                    href = link.get("href", "")
                    if href.endswith(VIDEO_EXTENSIONS):
                        quality_text = link.get_text(strip=True)
                        size_match = re.search(r"([\d.]+)\s*(GB|MB)", current.get_text())
                        size = f"{size_match.group(1)}{size_match.group(2)}" if size_match else None

                        if "versions" not in movie:
                            movie["versions"] = []

                        movie["versions"].append({
                            "url": href,
                            "quality_label": quality_text,
                            "size": size,
                            "sub_type": current_subtype,
                        })

            current = current.next_sibling

        if movie.get("title") and movie.get("versions"):
            return movie
        return None

    def _parse_movie_section(self, h3):
        movie = {}
        text = h3.get_text(strip=True)
        match = re.match(r"^\d+\.\s*(.+?)\s*start_year$", text)
        if match:
            movie["title"] = match.group(1).strip()

        current = h3.find_next_sibling()
        current_subtype = None

        while current and current.name != "hr":
            if current.name == "p":
                text = current.get_text(strip=True)

                if "IMDb Code:" in text:
                    imdb_match = re.search(r"tt\d+", text)
                    if imdb_match:
                        movie["imdb_id"] = imdb_match.group(0)

                if "IMDb Votes:" in text:
                    votes_match = re.search(r"([\d,]+)", text.split("IMDb Votes:")[1])
                    if votes_match:
                        movie["votes"] = votes_match.group(1).replace(",", "")

                if "IMDb Rates:" in text:
                    rate_match = re.search(r"([\d.]+)", text.split("IMDb Rates:")[1])
                    if rate_match:
                        movie["rating"] = rate_match.group(1)

                # Detect sub-type marker (SoftSub/Dubbed) - propagate to subsequent versions
                bold_tag = current.find("b")
                has_bold = bold_tag is not None
                has_link = current.find("a", href=True) is not None

                if has_bold and not has_link:
                    bold_text = bold_tag.get_text(strip=True)
                    # Only update subtype for actual subtype markers, not metadata labels
                    if bold_text in ("SoftSub", "NoSub", "Dubbed"):
                        current_subtype = bold_text

                link = current.find("a", href=True)
                if link:
                    href = link.get("href", "")
                    if href.endswith(VIDEO_EXTENSIONS):
                        quality_label = link.get_text(strip=True)
                        size_match = re.search(r"([\d.]+)\s*(GB|MB)", current.get_text())
                        size = f"{size_match.group(1)}{size_match.group(2)}" if size_match else None

                        if "versions" not in movie:
                            movie["versions"] = []

                        movie["versions"].append({
                            "url": href,
                            "quality_label": quality_label,
                            "size": size,
                            "sub_type": current_subtype,
                        })

            current = current.find_next_sibling()

        if movie.get("title") and movie.get("versions"):
            year_match = re.search(r"(19|20)\d{2}", movie.get("title", "") + " " + str(movie.get("versions")))
            if year_match:
                movie["year"] = year_match.group(0)

            if not movie.get("imdb_id"):
                for v in movie["versions"]:
                    imdb_match = re.search(r"/(tt\d+)/", v["url"])
                    if imdb_match:
                        movie["imdb_id"] = imdb_match.group(1)
                        break

            return movie

        return None

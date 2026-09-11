from datetime import datetime
import requests
import time


class VinylRecordsDashUtilities:
    def __init__(self, data):
        self.data = data
        self.artist_name = self.data['artist_name']
        self.record_name = None
        self.image_cover = None
        self.duration = None
        self.qt_lps = None
        self.release_year = None
        self.compilation = None
        self.artist_id = None
        self.release_group_result = None
        
    def get_artist_id(self):
        headers = {
                "User-Agent": f"MinhaColecaoMusical/1.0 (b{datetime.today().strftime('%d%m%y%H%M%S')}@exemplo.com)",
                "Accept": "application/json",
            }
        response = requests.get(
            "https://musicbrainz.org/ws/2/artist/",
            params={
                "query": f'artist:"{self.artist_name}"',
                "fmt": "json",
                "limit": 10,
            },
            headers = headers,
            timeout=150,
        )
        print(headers)

        response.raise_for_status()
        all_results =  [
            {
                "id": artist.get("id"),
                "name": artist.get("name"),
            }
            for artist in response.json().get("artists", [])
        ]
        result = [r for r in all_results if r['name'].lower().strip() == self.artist_name.lower().strip()][0]
        self.artist_id = result['id']

    def get_album_cover(self):
        get_cover = requests.get(f"https://coverartarchive.org/release/{self.album_id}")
        print(get_cover.text)
        self.image_cover = [i['image'] for i in get_cover.json()['images'] if i['approved'] and not i['back']][0]

    def get_release_group(self):
        try:
            self.get_artist_id()
            print(self.artist_id)
            time.sleep(2)
            response = requests.get(
                "https://musicbrainz.org/ws/2/release-group",
                params={
                    "artist": self.artist_id,
                    "type": "album",
                    "release-group-status": "website-default",
                    "fmt": "json",
                    "limit": 100,
                },
                headers = {
                    "User-Agent": f"MinhaColecaoMusical/1.0 (b{datetime.today().strftime('%d%m%y%H%M%S')}@exemplo.com)",
                    "Accept": "application/json",
                },
                timeout=30,
            )

            response.raise_for_status()

            albums = response.json().get("release-groups", [])

            albums.sort(
                key=lambda album: album.get("first-release-date") or "9999"
            )

            self.release_group_result = [
                {
                    "id": album["id"],
                    "title": album["title"],
                    "date": album.get("first-release-date"),
                    "type": album.get("primary-type"),
                    "secondary_types": album.get("secondary-types") or [],
                }
                for album in albums
            ]
        except Exception as e:
            print(e)
            self.release_group_result = [
            {
                "id": None,
                "title": None,
                "date": None,
                "type": None,
                "secondary_types": [],
            }
        ]
        return self.release_group_result

    def format_duration(self, milliseconds):
        if milliseconds is None:
            return None

        seconds = milliseconds // 1000
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"

        return f"{minutes}:{seconds:02d}"


    def get_album_details(self):
        release_group_id = self.data['release_group_id']
        try:
            response = requests.get(
                "https://musicbrainz.org/ws/2/release",
                params={
                    "release-group": release_group_id,
                    "status": "official",
                    "inc": "media+recordings+labels",
                    "fmt": "json",
                    "limit": 100,
                },
                headers = {
                    "User-Agent": f"MinhaColecaoMusical/1.0 (b{datetime.today().strftime('%d%m%y%H%M%S')}@exemplo.com)",
                    "Accept": "application/json",
                },
                timeout=30,
            )

            response.raise_for_status()

            releases = response.json().get("releases") or []

            if not releases:
                return None

            releases_with_media = [
                release
                for release in releases
                if release.get("media")
            ]

            if not releases_with_media:
                return None

            release = min(
                releases_with_media,
                key=lambda item: item.get("date") or "9999"
            )

            media = release.get("media") or []

            track_lengths = [
                track["length"]
                for disk in media
                for track in disk.get("tracks") or []
                if track.get("length") is not None
            ]

            duration_ms = sum(track_lengths) if track_lengths else None

            labels = [
                item["label"]["name"]
                for item in release.get("label-info") or []
                if (item.get("label") or {}).get("name")
            ]
            try:
                self.album_id = release.get("id")
                self.get_album_cover()
            except:
                pass

            return {
                "release_id": release.get("id"),
                "title": release.get("title"),
                "release_date": release.get("date"),
                "country": release.get("country"),
                "discs_quantity": len(media),
                "tracks_quantity": sum(
                    disk.get("track-count") or 0
                    for disk in media
                ),
                "formats": [
                    disk.get("format")
                    for disk in media
                    if disk.get("format")
                ],
                "duration": self.format_duration(duration_ms),
                "duration_ms": duration_ms,
                "labels": labels,
                "barcode": release.get("barcode"),
                "image_cover": self.image_cover
            }
        except:
            return {
                "release_id": None,
                "title": None,
                "release_date": None,
                "country": None,
                "discs_quantity": None,
                "tracks_quantity": None,
                "formats": None,
                "duration": None,
                "duration_ms": None,
                "labels": None,
                "barcode": None,
                "image_cover": None
            }

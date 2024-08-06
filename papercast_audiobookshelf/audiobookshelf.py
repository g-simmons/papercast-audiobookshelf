import os
from pathlib import Path
import requests
from typing import Optional, Iterable, Union

from papercast.production import Production
from papercast.base import BasePublisher
from papercast.types import (
    MOBIFile,
    AZW3File,
    CBRFile,
    CBZFile,
    NFOFile,
    TXTFile,
    OPFFile,
    ABSFile,
    TxtFile,
    SRTFile,
    M4BFile,
    M4AFile,
    PNGFile,
    JPGFile,
    JPEGFile,
    WEBPFile,
    M4BFile,
    MP3File,
    M4AFile,
    FLACFile,
    OPUSFile,
    OGGFile,
    OGAFile,
    MP4File,
    AACFile,
    WMAFile,
    AIFFFile,
    WAVFile,
    WEBMFile,
    WEBMAFile,
    EPUBFile,
    PDFFile,
    MOBIFile,
    AZW3File,
    CBRFile,
    CBZFile,
    NFOFile,
    TXTFile,
    OPFFile,
    ABSFile,
    TxtFile,
    SRTFile,
    M4BFile,
    M4AFile,
)

AudioBookShelfFile = Union[
    MOBIFile,
    AZW3File,
    CBRFile,
    CBZFile,
    NFOFile,
    TXTFile,
    OPFFile,
    ABSFile,
    TxtFile,
    SRTFile,
    M4BFile,
    M4AFile,
    PNGFile,
    JPGFile,
    JPEGFile,
    WEBPFile,
    M4BFile,
    MP3File,
    M4AFile,
    FLACFile,
    OPUSFile,
    OGGFile,
    OGAFile,
    MP4File,
    AACFile,
    WMAFile,
    AIFFFile,
    WAVFile,
    WEBMFile,
    WEBMAFile,
    EPUBFile,
    PDFFile,
    MOBIFile,
    AZW3File,
    CBRFile,
    CBZFile,
    NFOFile,
    TXTFile,
    OPFFile,
    ABSFile,
    TxtFile,
    SRTFile,
    M4BFile,
    M4AFile,
]


class AudioBookShelfProduction(Production):
    """
    See: https://api.audiobookshelf.org/#upload-files

    To get your library id, visit a library in the browser and copy the id from the URL.

    Example:
    https://<base_url>/library/lib_lcd3d5o2s2wxx90y38 - lib_lcd3d5o2s2wxx90y38 is the library id.

    Series is the string name of the series, not the id.

    To get your folder id, you need to query the api for your library and inspect the resulting information.

    curl "https://<base_url>/api/libraries/<library-id>?include=filterdata" \
        -H "Authorization: Bearer <your-audiobookshelf-api-token>"

    For example using jq to get the id of the first folder:

    curl "https://<base_url>/api/libraries/<library-id>?include=filterdata" \
        -H "Authorization: Bearer <your-audiobookshelf-api-token>" | jq '.library.folders[0].id'
    
    Should return a string like: "fol_hhky4gdeutrlj2c68x". This is the folder id.

    """

    title: str
    # description: Optional[str] = None
    library_id: str
    folder_id: str
    author: Optional[str] = None
    series: Optional[str] = None
    files: Iterable[AudioBookShelfFile]


class AudioBookShelfPublisher(BasePublisher):

    input_types = {
        "mp3_path": Path,
        "title": str,
        "library": str,
        "author": str,
        "series": str,
        "files": Iterable[AudioBookShelfFile],
        "description": str,
    }

    def __init__(
        self,
        token: str,
        base_url: str,
        default_metadata: dict = {},
    ) -> None:
        """
        Initialize the AudioBookShelfPublisher.

        Args:
            token (str): The authentication token for the AudioBookShelf API.
            base_url (str): The base URL of the AudioBookShelf API.

        Note:
            This publisher uses token-based authentication. Username and password
            authentication  may be implemented in future versions.
        """
        self.token = token
        self.base_url = base_url
        self.default_metadata = default_metadata

    # def _login(self) -> None:
    #     raise NotImplementedError("Login not implemented.")
    #     response = requests.post(
    #         f"{self.base_url}/login",
    #         headers={"Content-Type": "application/json"},
    #         data={"username": self.get_username(), "password": self.get_password()},
    #     )

    #     response.raise_for_status()

    #     self.token = response.json()["user"]["token"]

    # def get_username(self) -> Union[str, None]:
    #     raise NotImplementedError("Username not implemented.")
    #     if hasattr(self, "username"):
    #         return self.username
    #     elif os.getenv("AUDIOBOOKSHELF_USERNAME"):
    #         return os.getenv("AUDIOBOOKSHELF_USERNAME")
    #     else:
    #         raise ValueError(
    #             "No username provided, and AUDIOBOOKSHELF_USERNAME not set."
    #         )

    # def get_password(self) -> Union[str, None]:
    #     raise NotImplementedError("Password not implemented.")
    #     if hasattr(self, "password"):
    #         return self.password
    #     elif os.getenv("AUDIOBOOKSHELF_PASSWORD"):
    #         return os.getenv("AUDIOBOOKSHELF_PASSWORD")
    #     else:
    #         raise ValueError(
    #             "No password provided, and AUDIOBOOKSHELF_PASSWORD not set."
    #         )

    def _upload_file(self, production: AudioBookShelfProduction) -> None:
        """
        Upload a file to AudioBookShelf.

        This method prepares a request with the production details and file paths,
        then sends a POST request to the AudioBookShelf API to upload the file(s).

        Args:
            production (AudioBookShelfProduction): The production to be uploaded,
                containing details like title, author, series, library, folder,
                and mp3 files.

        Raises:
            requests.HTTPError: If the API request fails.

        Note:
            This method assumes that the `production` object has an `files`
            attribute, which should be an iterable of objects with a `path` attribute.
        """
        request = {
            "title": production.title,
            "author": getattr(production, "author", None),
            "series": getattr(production, "series", None),
            "library": getattr(production, "library_id", None),
            "folder": getattr(production, "folder_id", None),
        }

        request.update(self.default_metadata)

        files = [
            (str(i), (Path(file.path).name, open(file.path, "rb")))
            for i, file in enumerate(production.files)
        ]

        response = requests.post(
            f"{self.base_url}/api/upload",
            headers={"Authorization": f"Bearer {self.token}"},
            data=request,
            files=files,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 404:
                raise ValueError(response.text)

    def process(self, production: AudioBookShelfProduction, **kwargs) -> Production:
        self._upload_file(production)
        return production

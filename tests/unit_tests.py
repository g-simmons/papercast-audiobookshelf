import sys
import pytest

sys.path.append("../papercast_audiobookshelf")

from papercast.publishers import AudioBookShelfPublisher
from papercast.base import Production
from papercast.types import MP3File


class TestAudioBookShelfPublisher:

    def test_init(self):
        publisher = AudioBookShelfPublisher(
            token="test",
            base_url="test",
        )

        assert publisher.token == "test"
        assert publisher.base_url == "test"

    def test_upload(self, mocker, tmp_path):
        mock_post = mocker.patch("requests.post")
        publisher = AudioBookShelfPublisher(
            token="token",
            base_url="base_url",
        )

        # Create a temporary MP3 file
        temp_mp3 = tmp_path / "test.mp3"
        temp_mp3.write_bytes(b"dummy mp3 content")

        production = Production(
            title="Test",
            author="Test",
            series="All Papers",
            library_id="lib_xxxx",
            folder_id="fol_xxxx",
            files=[
                MP3File(
                    path=str(temp_mp3),
                )
            ],
            description="A programmatic upload test",
        )

        publisher.process(production=production)

        mock_post.assert_called_once()

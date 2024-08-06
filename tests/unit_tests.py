import sys
import pytest

sys.path.append("../papercast_audiobookshelf")

from audiobookshelf import AudioBookShelfPublisher


class TestAudioBookShelfPublisher:

    def test_init(self):
        publisher = AudioBookShelfPublisher(
            token="test",
            base_url="test",
        )

        assert publisher.token == "test"
        assert publisher.base_url == "test"

    def test_upload(self):
        publisher = AudioBookShelfPublisher(
            token="token",
            base_url="base_url",
        )

        production = AudioBookShelfProduction(
            title="Test",
            author="Test",
            series="All Papers",
            library_id="lib_xxxx",
            folder_id="fol_xxxx",
            files=[
                MP3File(
                    path="/path/to/mp3.mp3",
                )
            ],
            description="A programmatic upload test",
        )

        publisher.process(
            production=production,
        )

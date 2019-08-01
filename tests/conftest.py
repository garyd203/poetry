import httpretty
import os
import pytest
import shutil
import tempfile

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

from tomlkit import parse

from poetry.config.config import Config
from poetry.utils._compat import Path
from poetry.utils.helpers import merge_dicts
from poetry.utils.toml_file import TomlFile


@pytest.fixture
def tmp_dir():
    dir_ = tempfile.mkdtemp(prefix="poetry_")

    yield dir_

    shutil.rmtree(dir_)


@pytest.fixture
def config_document():
    content = """cache-dir = "/foo"
"""
    doc = parse(content)

    return doc


@pytest.fixture
def config_source(config_document, mocker):
    file = TomlFile(Path(tempfile.mktemp()))
    mocker.patch.object(file, "exists", return_value=True)
    mocker.patch.object(file, "read", return_value=config_document)
    mocker.patch.object(
        file, "write", return_value=lambda new: merge_dicts(config_document, new)
    )
    mocker.patch(
        "poetry.config.config_source.ConfigSource.file",
        new_callable=mocker.PropertyMock,
        return_value=file,
    )


@pytest.fixture
def config(config_source):
    c = Config()

    return c


def mock_clone(_, source, dest):
    # Checking source to determine which folder we need to copy
    parts = urlparse.urlparse(source)

    folder = (
        Path(__file__).parent.parent
        / "fixtures"
        / "git"
        / parts.netloc
        / parts.path.lstrip("/").rstrip(".git")
    )

    shutil.rmtree(str(dest))
    shutil.copytree(str(folder), str(dest))


@pytest.fixture
def tmp_dir():
    dir_ = tempfile.mkdtemp(prefix="poetry_")

    yield dir_

    shutil.rmtree(dir_)


@pytest.fixture
def environ():
    original_environ = dict(os.environ)

    yield

    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture(autouse=True)
def git_mock(mocker):
    # Patch git module to not actually clone projects
    mocker.patch("poetry.vcs.git.Git.clone", new=mock_clone)
    mocker.patch("poetry.vcs.git.Git.checkout", new=lambda *_: None)
    p = mocker.patch("poetry.vcs.git.Git.rev_parse")
    p.return_value = "9cf87a285a2d3fbb0b9fa621997b3acc3631ed24"


@pytest.fixture
def http():
    httpretty.enable()

    yield httpretty

    httpretty.disable()


@pytest.fixture
def fixture_dir():
    def _fixture_dir(name):
        return Path(__file__).parent / "fixtures" / name

    return _fixture_dir

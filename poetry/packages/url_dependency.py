import hashlib
import io

from pkginfo.distribution import HEADER_ATTRS
from pkginfo.distribution import HEADER_ATTRS_2_0
from poetry.utils._compat import urlparse

from .dependency import Dependency

# Patching pkginfo to support Metadata version 2.1 (PEP 566)
HEADER_ATTRS.update(
    {"2.1": HEADER_ATTRS_2_0 + (("Provides-Extra", "provides_extra", True),)}
)


class URLDependency(Dependency):
    def __init__(
        self,
        name,
        url,  # type: str
        category="main",  # type: str
        optional=False,  # type: bool
    ):
        self._url = url

        parsed = urlparse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("{} does not seem like a valid url".format(url))

        super(URLDependency, self).__init__(
            name, "*", category=category, optional=optional, allows_prereleases=True
        )

    @property
    def url(self):
        return self._url

    @property
    def base_pep_508_name(self):  # type: () -> str
        requirement = self.pretty_name

        if self.extras:
            requirement += "[{}]".format(",".join(self.extras))

        requirement += " @ {}".format(self._url)

        return requirement

    def is_url(self):  # type: () -> bool
        return True

"""Which product version a document describes.

The manual exists twice over. The version 2 and version 3 pages for a topic are worded almost
identically and differ in substance, so similarity alone returns the wrong one: a question about
version 3 matches the version 2 page nearly as well, and the answer that comes back is confidently
wrong. Filtering on this field before ranking is the fix, and it is the reason the retrieval work
in week 2 is more than an exercise.

The version is read from the filename, which is how the manual arrives from the documentation
team: `manual-v3-connection-timeout.md`. A document with no version in its name carries `None` and
is treated as applying to every version.
"""

import re

KNOWN_VERSIONS = ("v2", "v3")

# A partition key cannot be NULL, so a page that applies to every version is stored under this
# label. app/retrieval/vector_store.py explains why that matters to the index.
ANY_VERSION = "any"

_IN_NAME = re.compile(r"(?:^|[-_])(v\d+)(?:[-_])")


def version_of(filename: str) -> str | None:
    """`manual-v3-retries.md` -> `"v3"`. Anything without a version in its name -> `None`."""
    match = _IN_NAME.search(filename)
    if match is None:
        return None
    return match.group(1)


def applicable_versions(version: str) -> set[str]:
    """Which stored version labels a search may return when the customer runs `version`.

    This is the whole version filter, in one function. Every store calls it before ranking, and
    a search that is given no version never calls it at all — there is nothing to apply.

    One thing here is easy to miss and expensive to get wrong. The obvious answer is `{version}`,
    and it passes the test that says version 2 material must not come back. It also quietly drops
    every page that carries no version, so a question about something version-independent returns
    nothing, which looks to the support desk exactly like a system that does not know its own
    manual. `ANY_VERSION` is the label those pages are stored under.

    Return the labels as they are stored.
    """
    return {version}

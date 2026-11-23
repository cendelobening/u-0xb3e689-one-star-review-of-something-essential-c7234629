#!/usr/bin/env python3
"""One-star review of something essential: sleep.

Writes a single-line, deadpan one-star review (at most 160 characters)
to /output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt).
Pure Python standard library only.
"""

import os
import stat
import sys
import tempfile

REVIEW = (
    "Sleep charges eight hours a night and returns nothing I can "
    "remember. I complained. It told me to sleep on it."
)

MAX_CHARS = 160


def validate(review):
    """Check the review meets the competition gate."""
    if not isinstance(review, str):
        raise ValueError("review must be a string")
    if not review.strip():
        raise ValueError("review must not be blank")
    if "\n" in review or "\r" in review:
        raise ValueError("review must be a single line")
    if len(review) > MAX_CHARS:
        raise ValueError(
            "review is %d characters, over the %d limit" % (len(review), MAX_CHARS)
        )
    if len(review) < 1:
        raise ValueError("review must be at least 1 character")


def main():
    try:
        validate(REVIEW)
    except ValueError as exc:
        print("invalid review: %s" % exc, file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "entry.txt")
        data = REVIEW.encode("utf-8")

        fd, tmp_path = tempfile.mkstemp(
            dir=out_dir, prefix=".entry-", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
            os.chmod(tmp_path, 0o644)
            os.replace(tmp_path, out_path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        # Read back and verify bytes + mode.
        with open(out_path, "rb") as fh:
            written = fh.read()
        if written != data:
            print("verification failed: bytes on disk differ", file=sys.stderr)
            return 1
        mode = stat.S_IMODE(os.stat(out_path).st_mode)
        if mode != 0o644:
            print(
                "verification failed: mode is %o, expected 644" % mode,
                file=sys.stderr,
            )
            return 1
    except OSError as exc:
        print("failed to write entry: %s" % exc, file=sys.stderr)
        return 1

    print("wrote %d characters to %s" % (len(REVIEW), out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())

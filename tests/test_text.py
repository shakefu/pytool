"""
Tests for pytool.text.
"""

import pytool


def test_wrap_empty():
    text = ""
    assert pytool.text.wrap(text) == ""


def test_wrap():
    text = """
                    This is a description and it is long and spans multiple
                    lines. Hooray.
                        It should be indented here and this long line should
                        work out well when rewrapped.
                    This should be unindented and also work well and should be
                    a long line but get rewrapped.

                    Here's some more whitespace:

                        This should work out nicely.

                        This should be a really long line that gets nicely
                        wrapped and stuff like that.

                            Even multiple indents should work out well, which I
                            really hope they do.
                    """
    text = pytool.text.wrap(text, width=70)
    assert text == (
        """\
This is a description and it is long and spans multiple lines. Hooray.
    It should be indented here and this long line should work out well
    when rewrapped.
This should be unindented and also work well and should be a long line
but get rewrapped.

Here's some more whitespace:

    This should work out nicely.

    This should be a really long line that gets nicely wrapped and
    stuff like that.

        Even multiple indents should work out well, which I really
        hope they do.
"""
    )


def test_wrap_preserves_first_line_whitespace():
    text = """
                This tool is used for managing all the splits in dev, test and
                production.
        """

    text = pytool.text.wrap(text, width=70)
    assert text == (
        "This tool is used for managing all the splits in dev, test and\nproduction.\n"
    )

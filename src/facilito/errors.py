"""
Codigo Facilito errors types.
"""


class ClientError(Exception):
    """
    Codigo Facilito client error.
    """


class ClientAlreadyLogged(Exception):
    """
    The Client already has initiated
    a login call which was successful.
    """


class LoginFailed(Exception):
    """
    The Client failed to connect.
    Given credentials might be wrong.
    """


class RegexError(Exception):
    """
    A regex failed to execute.
    """


class URLError(Exception):
    """
    Provided URL is invalid.
    """


class ParsingError(Exception):
    """
    The parser failed to properly
    fetch data.
    """


class MaxRetriesExceeded(Exception):
    """
    A module failed its job after too
    many retries. You might want to
    try again after a little time.

    You can also use: attr:`Client.delay`
    to slow down requests.
    """


class UserNotFound(Exception):
    """
    User wasn't found. This either happens
    because the user does not exist, or
    its name or URL is wrong.
    """


class NoResult(Exception):
    """
    No result was found.
    """


class VideoError(Exception):
    """
    Codigo Facilito refused to serve video data because
    of some internal error (mostly because the video
    is not available anymore).
    """


class CourseError(Exception):
    """
    Codigo Facilito refused to serve course data because
    of some internal error (mostly because the course
    is not available anymore).
    """


class DownloadError(Exception):
    """
    Downloading video failed.
    """

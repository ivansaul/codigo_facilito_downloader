"""Error handling for Facilito API"""


class FacilitoApiError(Exception):
    """Raised when the API encounters an error"""


class FacilitoVideoNotAvailableError(FacilitoApiError):
    """Raised when the video is not available"""


class FacilitoCourseSectionNotExpandedError(FacilitoApiError):
    """Raised when the module is not expanded"""


class FacilitoMediaTypeError(FacilitoApiError):
    """Raised when the media type is not supported"""

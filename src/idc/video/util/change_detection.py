import cv2

from typing import Tuple

CONVERSION_GRAY = "gray"
CONVERSION_RED = "r"
CONVERSION_GREEN = "g"
CONVERSION_BLUE = "b"
CONVERSIONS = [
    CONVERSION_GRAY,
    CONVERSION_RED,
    CONVERSION_GREEN,
    CONVERSION_BLUE,
]


def to_single_channel(img, conversion: str = CONVERSION_GRAY):
    """
    Converts the image to a single channel.

    :param img: the image to convert
    :param conversion: how to convert the BGR image (gray/r/g/b)
    :type conversion: str
    :return: the single channel image
    """
    if conversion not in CONVERSIONS:
        raise Exception("Unknown conversion: %s" % conversion)
    if conversion == "gray":
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif conversion == "b":
        return img[:, :, 0]
    elif conversion == "g":
        return img[:, :, 1]
    elif conversion == "r":
        return img[:, :, 2]
    else:
        raise Exception("Unhandled conversion: %s" % conversion)


def diff_img(img1, img2):
    """
    Computes the absolute difference between two images.

    :param img1: the first image
    :param img2: the second image
    """
    return cv2.absdiff(img1, img2)


def to_bw(img, threshold):
    """
    Turns the gray image into binary.

    :param img: the image to convert
    :param threshold: the threshold to use
    :type threshold: int
    :return: the binary image
    """
    thresh, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return binary


def count_diff(img) -> int:
    """
    Counts the non-zero pixels in the image.

    :param img: the image to process
    :return: the count
    :rtype: int
    """
    return cv2.countNonZero(img)


def detect_change(img1, img2, conversion, bw_threshold, change_threshold: float) -> Tuple[float, bool]:
    """
    Returns true if there was change detected between the two images (turns them into gray images first).

    :param img1: the first image
    :param img2: the second image
    :param conversion: how to convert the BGR image (gray/r/g/b)
    :type conversion: str
    :param bw_threshold: the black/white threshold (0-255)
    :type bw_threshold: int
    :param change_threshold: the threshold for changes (0-1)
    :type change_threshold: float
    :return: the detected ratio, whether change was detected
    :rtype threshold: (float, bool)
    """
    size = img1.size
    img1 = to_single_channel(img1, conversion)
    img2 = to_single_channel(img2, conversion)
    count = count_diff(to_bw(diff_img(img1, img2), bw_threshold))
    ratio = float(count) / float(size)
    return ratio, ratio > change_threshold

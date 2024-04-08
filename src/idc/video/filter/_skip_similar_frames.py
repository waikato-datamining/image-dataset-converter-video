import argparse
import cv2
import numpy as np
from typing import List

from seppl.io import Filter
from wai.logging import LOGGING_WARNING
from idc.api import flatten_list, make_list, ImageData, ImageClassificationData, ImageSegmentationData, ObjectDetectionData
from idc.video.util.change_detection import CONVERSION_GRAY, CONVERSIONS, detect_change


class SkipSimilarFrames(Filter):
    """
    Skips frames in the stream that are deemed too similar.
    """

    def __init__(self, conversion: str = CONVERSION_GRAY, bw_threshold: int = 128,
                 change_threshold: float = 0.01,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param conversion: how to convert the BGR frames before calculating the changes
        :type conversion: str
        :param bw_threshold: the black/white threshold to use (0-255)
        :type bw_threshold: int
        :param change_threshold: the ratio of pixels that changed relative to size of image (0-1)
        :type change_threshold: float
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.conversion = conversion
        self.bw_threshold = bw_threshold
        self.change_threshold = change_threshold
        self._last_image = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "skip-similar-frames"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Skips frames in the stream that are deemed too similar."

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData, ImageSegmentationData, ObjectDetectionData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-c", "--conversion", choices=CONVERSIONS, default=CONVERSION_GRAY, help="How to convert the BGR image to a single channel image.", required=False)
        parser.add_argument("-b", "--bw_threshold", type=int, help="The threshold to use for converting a gray-scale like image to black and white (0-255).", required=False, default=128)
        parser.add_argument("-t", "--change_threshold", type=float, help="The ratio of pixels that changed relative to size of image (0-1).", required=False, default=0.01)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.conversion = ns.conversion
        self.bw_threshold = ns.bw_threshold
        self.change_threshold = ns.change_threshold

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.conversion is None:
            self.conversion = CONVERSION_GRAY
        if self.bw_threshold is None:
            self.bw_threshold = 128
        if self.change_threshold is None:
            self.change_threshold = 0.01
        self._last_image = None

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []
        for item in make_list(data):
            # read image
            img = cv2.cvtColor(np.array(item.image), cv2.COLOR_RGB2BGR)

            # nothing to compare against?
            if self._last_image is None:
                # shift state
                self._last_image = img
                continue

            # detect change
            ratio, changed = detect_change(self._last_image, img,
                                           self.conversion, self.bw_threshold, self.change_threshold)
            self.logger().info("%s (ratio/changed): %f -> %s" % (item.image_name, ratio, str(changed)))

            if changed:
                # shift state
                self._last_image = img
                result.append(item)

        return flatten_list(result)

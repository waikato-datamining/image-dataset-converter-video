import argparse
from typing import List

from seppl.io import Filter
from wai.logging import LOGGING_WARNING
from idc.api import flatten_list, make_list, ImageData, ImageClassificationData, ImageSegmentationData, ObjectDetectionData


class DropFrames(Filter):
    """
    Drops frames from the stream.
    """

    def __init__(self, nth_frame: int = -1, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param nth_frame: the nth frame to select
        :type nth_frame: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.nth_frame = nth_frame
        self._count = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "drop-frames"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Drops frames from the stream."

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
        parser.add_argument("-n", "--nth_frame", type=int, help="Which nth frame to drop, e..g, '2' means to drop every 2nd frame; passes frames through if <=1.", default=-1, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.nth_frame = ns.nth_frame

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._count = 0

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []

        for item in make_list(data):
            if item is not None:
                self._count += 1
                if (self._count % self.nth_frame) != 0:
                    result.append(item)

        return flatten_list(result)

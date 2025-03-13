import argparse
import cv2
import numpy as np
from typing import List

from wai.logging import LOGGING_WARNING
from idc.api import ImageData, StreamWriter, make_list
from seppl.placeholders import placeholder_list, InputBasedPlaceholderSupporter


class VideoFileWriter(StreamWriter, InputBasedPlaceholderSupporter):
    """
    Saves the incoming images as frames in the specified MJPEG file.
    """

    def __init__(self, output_file: str = None, fps: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param output_file: the MJPEG file to write the frames to
        :type output_file: str
        :param fps: the frames per second to use for the video
        :type fps: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.output_file = output_file
        self.fps = fps
        self._out = None
        self._last_output_file = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "to-video-file"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Saves the incoming images as frames in the specified MJPEG file."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output_file", type=str, help="The MJPEG file to save the incoming frames to. " + placeholder_list(obj=self), required=True)
        parser.add_argument("-f", "--fps", metavar="FPS", type=int, default=25, help="The frames-per-second to use for the video.", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.output_file = ns.output_file
        self.fps = ns.fps

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.fps is None:
            self.fps = 25

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        for item in make_list(data):
            output_file = self.session.expand_placeholders(self.output_file)
            if (self._out is None) or (output_file != self._last_output_file):
                self._close_stream()
                w, h = item.image.size
                self._out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, (w, h))
                self._last_output_file = output_file

            img = cv2.cvtColor(np.array(item.image), cv2.COLOR_RGB2BGR)
            self._out.write(img)

    def _close_stream(self):
        """
        Closes the output stream.
        """
        if self._out is not None:
            try:
                self._out.release()
            except:
                pass
            self._out = None

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self._close_stream()

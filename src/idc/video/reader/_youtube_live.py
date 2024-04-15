import argparse
import logging

import cv2
import os
from typing import List, Iterable

from wai.logging import LOGGING_WARNING
from vidgear.gears import CamGear

from idc.api import DATATYPES, data_type_to_class, ImageData, Reader, FORMAT_JPEG


class YoutubeLiveReader(Reader):
    """
    Reads frames from a Youtube live stream.
    """

    def __init__(self, url: str = None, resolution: str = None, from_frame: int = None, to_frame: int = None,
                 nth_frame: int = None, max_frames: int = None, prefix: str = None,
                 data_type: str = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param url: the Youtube URL to read from
        :type url: str
        :param resolution: the specific resolution to use
        :type resolution: str
        :param from_frame: the index of the first frame to use
        :type from_frame: int
        :param to_frame: the index of the last frame to use
        :type to_frame: int
        :param nth_frame: determines whether frames get skipped
        :type nth_frame: int
        :param max_frames: the maximum number of frames to read
        :type max_frames: int
        :param data_type: the type of output to generate from the images
        :type data_type: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.url = url
        self.resolution = resolution
        self.data_type = data_type
        self.from_frame = from_frame
        self.to_frame = to_frame
        self.nth_frame = nth_frame
        self.max_frames = max_frames
        self.prefix = prefix
        self._cap = None
        self._frame_no = None
        self._frame_count = None
        self._inputs = None
        self._current_input = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "from-youtube-live"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads frames from a Youtube live stream."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--youtube_url", type=str, default=None, help="The Youtube live stream URL to read from.", required=True)
        parser.add_argument("-r", "--resolution", type=str, default="best", help="The resolution to use, e.g., '480p' or 'best'.", required=False)
        parser.add_argument("-t", "--data_type", choices=DATATYPES, type=str, default=None, help="The type of data to forward", required=True)
        parser.add_argument("-F", "--from_frame", type=int, default=1, help="Determines with which frame to start the stream (1-based index).", required=False)
        parser.add_argument("-T", "--to_frame", type=int, default=-1, help="Determines after which frame to stop (1-based index); ignored if <=0.", required=False)
        parser.add_argument("-n", "--nth_frame", type=int, default=1, help="Determines whether frames get skipped and only evert nth frame gets forwarded.", required=False)
        parser.add_argument("-m", "--max_frames", type=int, default=-1, help="Determines the maximum number of frames to read; ignored if <=0.", required=False)
        parser.add_argument("-p", "--prefix", type=str, help="The prefix to use for the frames", required=False, default="youtube-")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.youtube_url = ns.youtube_url
        self.resolution = ns.resolution
        self.data_type = ns.data_type
        self.from_frame = ns.from_frame
        self.to_frame = ns.to_frame
        self.nth_frame = ns.nth_frame
        self.max_frames = ns.max_frames
        self.prefix = ns.prefix

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        if self.data_type is None:
            return [ImageData]
        else:
            return [data_type_to_class(self.data_type)]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.youtube_url is None:
            raise Exception("No Youtube URL defined!")
        if self.data_type is None:
            raise Exception("No data type defined!")
        if (self.from_frame is None) or (self.from_frame < 0):
            self.from_frame = 1
        if self.to_frame is None:
            self.to_frame = -1
        if self.nth_frame is None:
            self.nth_frame = 1
        if self.nth_frame < 1:
            raise Exception("nth_frame must be at least 1, provided: %d" % self.nth_frame)
        if self.max_frames is None:
            self.max_frames = -1
        if self.prefix is None:
            self.prefix = ""
        if self.resolution is None:
            self.resolution = "best"
        self._inputs = [self.youtube_url]

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        self._current_input = self._inputs.pop(0)
        self.session.current_input = self.prefix + str(self._current_input)
        self.logger().info("Reading from Youtube: " + str(self._current_input))
        logging_on = self.logger().level < logging.WARNING

        self._cap = CamGear(source=self._current_input, stream_mode=True,
                            STREAM_RESOLUTION=self.resolution,
                            time_delay=1, logging=logging_on).start()
        self._frame_no = 0
        self._frame_count = 0

        cls = data_type_to_class(self.data_type)

        # next frame?
        count = 0
        while self._cap is not None:
            # next frame
            self._frame_no += 1
            count += 1
            frame_curr = self._cap.read()

            if frame_curr is not None:
                # within frame window?
                if self.from_frame > 0:
                    if self._frame_no < self.from_frame:
                        continue
                if self.to_frame > 0:
                    if self._frame_no >= self.to_frame:
                        break

                # skip frame?
                if (self.nth_frame > 1) and (count < self.nth_frame):
                    continue

                # max frames reached?
                if (self.max_frames > 0) and (self._frame_count >= self.max_frames):
                    break

                self._frame_count += 1
                count = 0
                data = cv2.imencode(".jpg", frame_curr)[1].tobytes()
                filename = os.path.join(
                    self.session.current_input,
                    "%s%08d.jpg" % (self.prefix, self._frame_no))
                height, width, _ = frame_curr.shape
                yield cls(source=filename, data=data, image_format=FORMAT_JPEG, image_size=(width, height))
            else:
                self._cap.release()
                self._cap = None

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0

    def finalize(self):
        """
        Finishes the reading, e.g., for closing files or databases.
        """
        if self._current_input is not None:
            super().finalize()
            # close video file
            if self._cap is not None:
                self._cap.stop()
                self._cap = None

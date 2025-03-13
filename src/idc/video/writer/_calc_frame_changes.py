import argparse
import csv
import cv2
import json
import numpy as np
import sys
import termplotlib as tpl

from typing import List

from wai.logging import LOGGING_WARNING
from idc.api import ImageData, StreamWriter, make_list
from idc.video.util.change_detection import CONVERSION_GRAY, CONVERSIONS, detect_change
from seppl.placeholders import placeholder_list, InputBasedPlaceholderSupporter


OUTPUT_FORMAT_TEXT = "text"
OUTPUT_FORMAT_CSV = "csv"
OUTPUT_FORMAT_JSON = "json"
OUTPUT_FORMATS = [
    OUTPUT_FORMAT_TEXT,
    OUTPUT_FORMAT_CSV,
    OUTPUT_FORMAT_JSON,
]


class CalcFrameChanges(StreamWriter, InputBasedPlaceholderSupporter):
    """
    Calculates the changes between frames, which can be used with the skip-similar-frames filter.
    """

    def __init__(self, conversion: str = CONVERSION_GRAY, bw_threshold: int = 128,
                 change_threshold: float = 0.01, num_bins: int = 20,
                 output_file: str = None, output_format: str = OUTPUT_FORMAT_TEXT,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param conversion: how to convert the BGR frames before calculating the changes
        :type conversion: str
        :param bw_threshold: the black/white threshold to use (0-255)
        :type bw_threshold: int
        :param change_threshold: the ratio of pixels that changed relative to size of image (0-1)
        :type change_threshold: float
        :param num_bins: the number of bins to use for the histogram
        :type num_bins: int
        :param output_file: the file to write the stats to
        :type output_file: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.conversion = conversion
        self.bw_threshold = bw_threshold
        self.change_threshold = change_threshold
        self.num_bins = num_bins
        self.output_file = output_file
        self.output_format = output_format
        self._last_image = None
        self._ratios = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "calc-frame-changes"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Calculates the changes between frames, which can be used with the skip-similar-frames filter."

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
        parser.add_argument("-B", "--num_bins", type=int, help="The number of bins to use for the histogram.", required=False, default=20)
        parser.add_argument("-o", "--output_file", type=str, help="The file to write to statistics to, stdout if not provided. " + placeholder_list(obj=self), required=False, default=None)
        parser.add_argument("-f", "--output_format", choices=OUTPUT_FORMATS, default=OUTPUT_FORMAT_TEXT, help="The format to use for the statistics.", required=False)
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
        self.num_bins = ns.num_bins
        self.output_file = ns.output_file
        self.output_format = ns.output_format

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
        if self.conversion is None:
            self.conversion = CONVERSION_GRAY
        if self.bw_threshold is None:
            self.bw_threshold = 128
        if self.change_threshold is None:
            self.change_threshold = 0.01
        if self.num_bins is None:
            self.num_bins = 20
        if self.output_format is None:
            self.output_format = OUTPUT_FORMAT_TEXT
        self._last_image = None
        self._ratios = []

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
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
            self.logger().debug("%s (ratio/changed): %f -> %s" % (item.image_name, ratio, str(changed)))

            if changed:
                # shift state
                self._last_image = img
                self._ratios.append(ratio)

    def output_stats(self):
        """
        Calculates and outputs the statistics.
        """
        if not hasattr(self, "_ratios"):
            self.logger().error("Not data collected for statistics!")
            return

        use_stdout = (self.output_file is None) or (len(self.output_file) == 0)
        output_file = (None if use_stdout else self.session.expand_placeholders(self.output_file))
        if output_file is not None:
            self.logger().info("Writing stats to: %s" % output_file)
        counts, bin_edges = np.histogram(self._ratios, bins=self.num_bins)

        # text
        if self.output_format == "text":
            fig = tpl.figure()
            fig.hist(counts, bin_edges, orientation="horizontal", force_ascii=False)
            if use_stdout:
                fig.show()
            else:
                with open(output_file, "w") as fp:
                    fp.write(fig.get_string())
                    fp.write("\n")

        # csv
        elif self.output_format == "csv":
            data = [["bin", "from", "to", "count"]]
            for i in range(self.num_bins):
                data.append([i, bin_edges[i], bin_edges[i+1], counts[i]])
            if use_stdout:
                writer = csv.writer(sys.stdout)
                writer.writerows(data)
            else:
                with open(output_file, "w") as fp:
                    writer = csv.writer(fp)
                    writer.writerows(data)

        # json
        elif self.output_format == "json":
            data = []
            for i in range(self.num_bins):
                data.append({
                    "bin": i,
                    "from": float(bin_edges[i]),
                    "to": float(bin_edges[i+1]),
                    "count": int(counts[i])
                })
            if use_stdout:
                print(json.dumps(data, indent=2))
            else:
                with open(output_file, "w") as fp:
                    json.dump(data, fp, indent=2)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.output_stats()

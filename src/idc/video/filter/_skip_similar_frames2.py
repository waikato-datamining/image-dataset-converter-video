import argparse
import statistics
from typing import List

import cv2
import numpy as np
from wai.logging import LOGGING_WARNING

from idc.api import ImageData, ImageClassificationData, ImageSegmentationData, ObjectDetectionData
from idc.filter import DiscardFilter
from kasperl.api import make_list, flatten_list


class SkipSimilarFrames2(DiscardFilter):
    """
    Skips frames in the stream that are deemed too similar.
    """

    def __init__(self, image_size: int = None, hash_size: int = None, hash_weight: float = None, threshold: float = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param image_size: the size to scale the images to (width and height)
        :type image_size: int
        :param hash_size: the hash size to use
        :type hash_size: int
        :param hash_weight: the weighting to give to the hash similarity of the mean absolute difference one (0-1)
        :type hash_weight: float
        :param threshold: the threshold to use for the similarity
        :type threshold: float
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.image_size = image_size
        self.hash_size = hash_size
        self.hash_weight = hash_weight
        self.threshold = threshold
        self._last_image = None
        self._similarities = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "skip-similar-frames2"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Skips frames in the stream that are deemed too similar: uses difference hash and mean absolute difference for calculating the similarity."

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
        parser.add_argument("-I", "--image_size", type=int, help="The size to scale the images to (width and height).", required=False, default=128)
        parser.add_argument("-H", "--hash_size", type=int, help="The size to use for the hash.", required=False, default=8)
        parser.add_argument("-w", "--hash_weight", type=float, help="The weighting to give to the hash similarity (0-1), the remainder is applied to the pixel similarity.", required=False, default=0.7)
        parser.add_argument("-t", "--threshold", type=float, help="The similarity threshold to use (0-1); an image is deemed too similar when achieving at least this score.", required=False, default=0.98)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.image_size = ns.image_size
        self.hash_size = ns.hash_size
        self.hash_weight = ns.hash_weight
        self.threshold = ns.threshold

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.image_size is None:
            self.image_size = 128
        if self.hash_size is None:
            self.hash_size = 8
        if self.hash_weight is None:
            self.hash_weight = 0.7
        if (self.hash_weight < 0) or (self.hash_weight > 1):
            raise Exception("Hash weight needs to be within 0-1, provided: %f" % self.hash_weight)
        if self.threshold is None:
            self.threshold = 0.98
        self._last_image = None
        self._similarities = []

    def _prepare_image(self, item) -> np.ndarray:
        """
        Prepares the image for the comparison.

        :param item: the image to prepare
        :return: the scaled gray image
        :rtype: np.ndarray
        """
        image = np.asarray(item.image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (self.image_size, self.image_size), interpolation=cv2.INTER_AREA)
        return gray

    def _dhash(self, gray: np.ndarray) -> np.ndarray:
        """
        Generates the difference hash: encode the horizontal gradient direction as a compact bit vector.
        Resize to (hash_size+1) x hash_size so each row produces hash_size comparison bits.

        :param gray: the gray image to process
        :type gray: np.ndarrau
        :return: the hash
        :rtype: np.ndarray
        """
        # Difference hash: encode the horizontal gradient direction as a compact bit vector.
        # Resize to (hash_size+1) x hash_size so each row produces hash_size comparison bits.
        resized = cv2.resize(gray, (self.hash_size + 1, self.hash_size), interpolation=cv2.INTER_AREA)
        diff = resized[:, 1:] > resized[:, :-1]
        return diff.flatten()

    def _similarity(self, gray_a: np.ndarray, gray_b: np.ndarray) -> float:
        """
        Computes the similarity between the two gray images.

        :param gray_a: the first scaled gray image
        :type gray_a: np.ndarray
        :param gray_b: the second scaled gray image
        :type gray_b: np.ndarray
        :return: the similarity score
        :rtype: float
        """
        hash_a = self._dhash(gray_a)
        hash_b = self._dhash(gray_b)
        hamming = float(np.count_nonzero(hash_a != hash_b))
        hash_similarity = 1.0 - (hamming / float(hash_a.size))

        # mean absolute difference normalized to [0, 1]; subtract from 1 to get similarity.
        mad = float(cv2.meanStdDev(cv2.absdiff(gray_a, gray_b))[0][0][0] / 255.0)
        pixel_similarity = 1.0 - mad

        return self.hash_weight * hash_similarity + (1.0 - self.hash_weight) * pixel_similarity

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []
        for item in make_list(data):
            # read image
            img = self._prepare_image(item)

            # nothing to compare against?
            if self._last_image is None:
                # shift state
                self._last_image = img
                continue

            similarity = self._similarity(img, self._last_image)
            self.logger().debug("%s similarity to previous image: %f" % (item.image_name, similarity))
            self._similarities.append(similarity)

            if similarity < self.threshold:
                # shift state
                self._last_image = img
                self._keep(item)
                result.append(item)
            else:
                self._discard(item)

        return flatten_list(result)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("min similarity: %f" % min(self._similarities))
        self.logger().info("max similarity: %f" % max(self._similarities))
        self.logger().info("mean similarity: %f" % statistics.mean(self._similarities))
        self.logger().info("stdev similarity: %f" % statistics.stdev(self._similarities))

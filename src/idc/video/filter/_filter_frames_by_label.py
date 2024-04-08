import argparse
from typing import List

from seppl.io import Filter
from wai.logging import LOGGING_WARNING

from idc.api import flatten_list, make_list, ObjectDetectionData, LABEL_KEY


class FilterFramesByLabel(Filter):
    """
    Filters frames from the stream using the labels in the annotations, i.e., keeps or drops frames depending on presence/absence of labels.
    """

    def __init__(self, key_label: str = LABEL_KEY, required_labels: str = None, excluded_labels: str = None,
                 key_score: str = None, min_score: float = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param key_label: the meta-data key in the annotations that contains the label.
        :type key_label: str
        :param required_labels: the comma-separated list of labels that must be present in the frame, otherwise it gets dropped
        :type required_labels: str
        :param excluded_labels: the comma-separated list of labels that will automatically drop the frame when present in the frame
        :type excluded_labels: str
        :param key_score: the meta-data key in the annotations to use for storing the prediction score.
        :type key_score: str
        :param min_score: the minimum score that predictions must have in order to be included in the label checks, ignored if not supplied
        :type min_score: float
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.key_label = key_label
        self.required_labels = required_labels
        self.excluded_labels = excluded_labels
        self.key_score = key_score
        self.min_score = min_score
        self._required_labels = None
        self._excluded_labels = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "filter-frames-by-label"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Filters frames from the stream using the labels in the annotations, i.e., keeps or drops frames depending on presence/absence of labels."

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ObjectDetectionData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ObjectDetectionData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("--key_label", type=str, help="The meta-data key in the annotations that contains the label.", default=LABEL_KEY, required=False)
        parser.add_argument("--required_labels", type=str, help="The comma-separated list of labels that must be present in the frame, otherwise it gets dropped.", default=None, required=False)
        parser.add_argument("--excluded_labels", type=str, help="The comma-separated list of labels that will automatically drop the frame when present in the frame.", default=None, required=False)
        parser.add_argument("--key_score", type=str, help="The meta-data key in the annotations to use for storing the prediction score.", default="score", required=False)
        parser.add_argument("--min_score", type=float, help="The minimum score that predictions must have in order to be included in the label checks, ignored if not supplied.", default=None, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.key_label = ns.key_label
        self.required_labels = ns.required_labels
        self.excluded_labels = ns.excluded_labels
        self.key_score = ns.key_score
        self.min_score = ns.min_score

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        if self.required_labels is None:
            self.required_labels = ""
        if len(self.required_labels) > 0:
            self._required_labels = set(self.required_labels.split(","))
        else:
            self._required_labels = None

        if self.excluded_labels is None:
            self.excluded_labels = ""
        if len(self.excluded_labels) > 0:
            self._excluded_labels = set(self.excluded_labels.split(","))
        else:
            self._excluded_labels = None

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []

        for item in make_list(data):
            ignored = set()

            # min score
            if (self.min_score is not None) and (self.min_score > 0):
                for index, obj in enumerate(item.annotation):
                    if self.key_score in obj.metadata:
                        if float(obj.metadata[self.key_score]) < self.min_score:
                            ignored.add(index)
                    else:
                        ignored.add(index)

                # remove objects
                if len(ignored) > 0:
                    self.logger().info(
                        "Ignoring %d annotation(s) due to min_score of %f" % (len(ignored), self.min_score))

            # check labels
            keep = False
            skip = False

            # 1. required labels
            if self._required_labels is not None:
                for index, obj in enumerate(item.annotation):
                    if index in ignored:
                        continue
                    if self.key_label in obj.metadata:
                        if str(obj.metadata[self.key_label]) in self._required_labels:
                            keep = True
                    else:
                        skip = True

            # 2. excluded labels
            if self._excluded_labels is not None:
                for index, obj in enumerate(item.annotation):
                    if index in ignored:
                        continue
                    if self.key_label in obj.metadata:
                        if str(obj.metadata[self.key_label]) in self._excluded_labels:
                            skip = True
                    else:
                        skip = True

            # drop frame?
            if skip or not keep:
                continue
            else:
                result.append(item)

        return flatten_list(result)

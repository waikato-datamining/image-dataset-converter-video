# filter-frames-by-label

* accepts: idc.api.ObjectDetectionData
* generates: idc.api.ObjectDetectionData

Filters frames from the stream using the labels in the annotations, i.e., keeps or drops frames depending on presence/absence of labels.

```
usage: filter-frames-by-label [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                              [-N LOGGER_NAME] [--key_label KEY_LABEL]
                              [--required_labels REQUIRED_LABELS]
                              [--excluded_labels EXCLUDED_LABELS]
                              [--key_score KEY_SCORE] [--min_score MIN_SCORE]

Filters frames from the stream using the labels in the annotations, i.e.,
keeps or drops frames depending on presence/absence of labels.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --key_label KEY_LABEL
                        The meta-data key in the annotations that contains the
                        label. (default: type)
  --required_labels REQUIRED_LABELS
                        The comma-separated list of labels that must be
                        present in the frame, otherwise it gets dropped.
                        (default: None)
  --excluded_labels EXCLUDED_LABELS
                        The comma-separated list of labels that will
                        automatically drop the frame when present in the
                        frame. (default: None)
  --key_score KEY_SCORE
                        The meta-data key in the annotations to use for
                        storing the prediction score. (default: score)
  --min_score MIN_SCORE
                        The minimum score that predictions must have in order
                        to be included in the label checks, ignored if not
                        supplied. (default: None)
```

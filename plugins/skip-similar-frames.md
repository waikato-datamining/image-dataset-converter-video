# skip-similar-frames

* accepts: idc.api.ImageData
* generates: idc.api.ImageClassificationData, idc.api.ImageSegmentationData, idc.api.ObjectDetectionData

Skips frames in the stream that are deemed too similar.

```
usage: skip-similar-frames [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                           [-N LOGGER_NAME] [--skip] [-c {gray,r,g,b}]
                           [-b BW_THRESHOLD] [-t CHANGE_THRESHOLD]

Skips frames in the stream that are deemed too similar.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -c {gray,r,g,b}, --conversion {gray,r,g,b}
                        How to convert the BGR image to a single channel
                        image. (default: gray)
  -b BW_THRESHOLD, --bw_threshold BW_THRESHOLD
                        The threshold to use for converting a gray-scale like
                        image to black and white (0-255). (default: 128)
  -t CHANGE_THRESHOLD, --change_threshold CHANGE_THRESHOLD
                        The ratio of pixels that changed relative to size of
                        image (0-1). (default: 0.01)
```

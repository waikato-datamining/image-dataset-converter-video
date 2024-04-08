# drop-frames

* accepts: idc.api.ImageData
* generates: idc.api.ImageClassificationData, idc.api.ImageSegmentationData, idc.api.ObjectDetectionData

Drops frames from the stream.

```
usage: drop-frames [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-n NTH_FRAME]

Drops frames from the stream.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -n NTH_FRAME, --nth_frame NTH_FRAME
                        Which nth frame to drop, e..g, '2' means to drop every
                        2nd frame; passes frames through if <=1. (default: -1)
```

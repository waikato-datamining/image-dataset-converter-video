# to-video-file

* accepts: idc.api.ImageData

Saves the incoming images as frames in the specified MJPEG file.

```
usage: to-video-file [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [-N LOGGER_NAME] -o OUTPUT_FILE [-f FPS]

Saves the incoming images as frames in the specified MJPEG file.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The MJPEG file to save the incoming frames to.
                        (default: None)
  -f FPS, --fps FPS     The frames-per-second to use for the video. (default:
                        25)
```

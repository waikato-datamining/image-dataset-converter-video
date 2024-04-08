# from-video-file

* generates: idc.api.ImageData

Reads frames from a video file.

```
usage: from-video-file [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] -i INPUT -t {ic,is,od} [-F FROM_FRAME]
                       [-T TO_FRAME] [-n NTH_FRAME] [-m MAX_FRAMES]
                       [-p PREFIX]

Reads frames from a video file.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i INPUT, --input INPUT
                        Path to the video file to read (default: None)
  -t {ic,is,od}, --data_type {ic,is,od}
                        The type of data to forward (default: None)
  -F FROM_FRAME, --from_frame FROM_FRAME
                        Determines with which frame to start the stream
                        (1-based index). (default: 1)
  -T TO_FRAME, --to_frame TO_FRAME
                        Determines after which frame to stop (1-based index);
                        ignored if <=0. (default: -1)
  -n NTH_FRAME, --nth_frame NTH_FRAME
                        Determines whether frames get skipped and only evert
                        nth frame gets forwarded. (default: 1)
  -m MAX_FRAMES, --max_frames MAX_FRAMES
                        Determines the maximum number of frames to read;
                        ignored if <=0. (default: -1)
  -p PREFIX, --prefix PREFIX
                        The prefix to use for the frames (default: )
```

# from-video-file

* generates: idc.api.ImageData

Reads frames from a video file.

```
usage: from-video-file [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-N LOGGER_NAME] [-i [INPUT ...]] [-I [INPUT_LIST ...]]
                       -t {ic,is,od} [-F FROM_FRAME] [-T TO_FRAME]
                       [-n NTH_FRAME] [-f FPS_FACTOR] [-m MAX_FRAMES]
                       [-p PREFIX]

Reads frames from a video file.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i [INPUT ...], --input [INPUT ...]
                        Path to the video file(s) to read; glob syntax is
                        supported; Supported placeholders: {HOME}, {CWD},
                        {TMP} (default: None)
  -I [INPUT_LIST ...], --input_list [INPUT_LIST ...]
                        Path to the text file(s) listing the video files to
                        read; Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
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
                        nth frame gets forwarded; <1 uses rounded up fraction
                        of frames-per-second in the video, e.g. 0.2 of video
                        with 25 fps results in every 5th frame being returned.
                        (default: 1)
  -f FPS_FACTOR, --fps_factor FPS_FACTOR
                        Multiplier applied to the frames-per-second (fps) of
                        the video and rounded up (ceiling) to determine the
                        actual nth frame to return; overrides -n/--nth_frame.
                        (default: None)
  -m MAX_FRAMES, --max_frames MAX_FRAMES
                        Determines the maximum number of frames to read;
                        ignored if <=0. (default: -1)
  -p PREFIX, --prefix PREFIX
                        The prefix to use for the frames (default: )
```

Available placeholders:

* `{HOME}`: The home directory of the current user.
* `{CWD}`: The current working directory.
* `{TMP}`: The temp directory.

# from-webcam

* generates: idc.api.ImageData

Reads frames from a webcam.

```
usage: from-webcam [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [-i WEBCAM_ID] -t {dp,ic,is,od}
                   [-F FROM_FRAME] [-T TO_FRAME] [-n NTH_FRAME]
                   [-m MAX_FRAMES] [-p PREFIX]

Reads frames from a webcam.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -i WEBCAM_ID, --webcam_id WEBCAM_ID
                        The ID of the webcam to read from. (default: 0)
  -t {dp,ic,is,od}, --data_type {dp,ic,is,od}
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
                        The prefix to use for the frames (default: webcam-)
```

The following data types are available:

* dp: depth
* ic: image classification
* is: image segmentation
* od: object detection


# skip-similar-frames2

* accepts: idc.api.ImageData
* generates: idc.api.ImageClassificationData, idc.api.ImageSegmentationData, idc.api.ObjectDetectionData

Skips frames in the stream that are deemed too similar: uses difference hash and mean absolute difference for calculating the similarity.

```
usage: skip-similar-frames2 [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                            [-N LOGGER_NAME] [--skip] [-I IMAGE_SIZE]
                            [-H HASH_SIZE] [-w HASH_WEIGHT] [-t THRESHOLD]

Skips frames in the stream that are deemed too similar: uses difference hash
and mean absolute difference for calculating the similarity.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --skip                Disables the plugin, removing it from the pipeline.
                        (default: False)
  -I IMAGE_SIZE, --image_size IMAGE_SIZE
                        The size to scale the images to (width and height).
                        (default: 128)
  -H HASH_SIZE, --hash_size HASH_SIZE
                        The size to use for the hash. (default: 8)
  -w HASH_WEIGHT, --hash_weight HASH_WEIGHT
                        The weighting to give to the hash similarity (0-1),
                        the remainder is applied to the pixel similarity.
                        (default: 0.7)
  -t THRESHOLD, --threshold THRESHOLD
                        The similarity threshold to use (0-1); an image is
                        deemed too similar when achieving at least this score.
                        (default: 0.98)
```

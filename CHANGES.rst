Changelog
=========

0.1.0 (2025-10-31)
------------------

- switched to `kasperl` library for base API and generic pipeline plugins


0.0.5 (2025-07-11)
------------------

- readers now set the `image_name` rather than the `source` to avoid errors when
  trying to determine the size of the extracted image


0.0.4 (2025-04-03)
------------------

- added `--resume_from` option to `from-video-file` reader that allows resuming the data processing
  from the first file that matches this glob expression (e.g., `*/012345.avi`)
- using underscores now instead of dashes in dependencies (`setup.py`)


0.0.3 (2025-03-14)
------------------

- added support for placeholders to: `from-video-file`, `calc-frame-changes`, and `to-video-file`


0.0.2 (2025-03-12)
------------------

- switched to underscores in project name
- `from-video-file` can process multiple files now and the `-f/--fps_factor` option
  can override the `-n/--nth_frame` option by calculation the nth frame based on
  the frame-rate of the video


0.0.1 (2024-05-06)
------------------

- initial release


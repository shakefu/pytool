# `pytool`: Python helper package

This package contains a lot of helpful little methods and functions to make
your life a little easier and your day a little better. Enjoy!

If you would like to see something added here, feel free to open up a
[GitHub issue](https://github.com/shakefu/pytool/issues).

## `pytool.cmd`: Command helpers

::: pytool.cmd
    options:
      show_root_heading: false
      members:
        - Command

## `pytool.json`: JSON helpers

::: pytool.json
    options:
      show_root_heading: false
      members:
        - as_json
        - from_json

## `pytool.lang`: Language helpers

::: pytool.lang
    options:
      show_root_heading: false
      members:
        - Namespace
        - Keyspace
        - UNSET
        - classproperty
        - get_name
        - hashed_singleton
        - singleton
        - unflatten

## `pytool.text`: Text helpers

::: pytool.text
    options:
      show_root_heading: false
      members:
        - wrap
        - columns

## `pytool.time`: Time and Date related helpers

::: pytool.time
    options:
      show_root_heading: false
      members:
        - Timer
        - UTC
        - as_utc
        - utcnow
        - fromutctimestamp
        - toutctimestamp
        - is_dst
        - trim_time
        - floor_day
        - floor_minute
        - floor_month
        - floor_week
        - make_week_seconds
        - week_seconds
        - week_seconds_to_datetime
        - week_start
        - ago

## `pytool.proxy`: DictProxy and ListProxy classes

::: pytool.proxy
    options:
      show_root_heading: false
      members:
        - DictProxy
        - ListProxy

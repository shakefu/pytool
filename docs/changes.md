# Changelog

## All releases

Release are now tracked
[on GitHub](https://github.com/shakefu/pytool/releases). Please visit there to
see changes from `3.4.2` and later.

## Older releases

Here you'll find a record of the changes in each version of `pytool`.

### 3.4.2

- Preserves `@staticmethod` functions on `pytool.lang.singleton` and
  `pytool.lang.hashed_singleton` decorated classes.

*Released March 19, 2018.*

### 3.4.1

- Merges the tests and fix from
  [PR #3](https://github.com/shakefu/pytool/pull/3). Thanks to
  [abendig](https://github.com/abendig) for the contribution.

*Released August 4, 2015.*

### 3.4.0

- Adds **Python 3** compatibility to Pytool! Hooray! Please submit an issue if
  you find any bugs in Python 3. Due to the dependency on `simplejson`, only
  Python 3.3 and later is supported.

*Released August 4, 2015.*

### 3.3.0

- Adds `pytool.time.ago`, which is a convenient helper for getting times
  relative to a timestamp or the current time.

*Released August 3, 2015.*

### 3.2.0

- Adds `pytool.text` and `pytool.text.wrap` which helps wrap text and remove or
  add indentation, and does so in a paragraph and whitespace aware fashion.
- Adds `pytool.cmd.Command.describe` to make it easier to add verbose
  descriptions to your command's `--help`.

### 3.1.1

- Depend on canonical version of simplejson again instead of github fork.

### 3.1.0

- Add `pytool.time.Timer` for easy timing of things.

### 3.0.1

- Fix bug with setup.py which broke installs.

### 3.0.0

- Changed to depend on simplejson (`>=3.2.0`) for the `_asdict()` and
  `for_json()` hooks. This may break backwards compatability.

### 2.4.1

- Fix bug where `for_json()` hook was ignored on classes that subclass the
  basic types.
- Fix bug where `pytool.json.as_json` would leave a trailing space on
  timestamps if there is no timezone associated with them.

### 2.4.0

- Improve documentation.
- Add `for_json()` hook in `pytool.json.as_json`.
- Add `__repr__()` to `pytool.time.UTC` to make it prettier.
- Add support for `_asdict()` hook (implemented by `namedtuple`) even when not
  using `simplejson`.
- Fix `pytool.time.is_dst` test.
- Add `for_json()` hook to `pytool.proxy.DictProxy` and
  `pytool.proxy.ListProxy`.

### 2.3.2

- Fix descriptor protocol in iteritems.

### 2.3.1

- Implement a instance-descriptor read-only protocol for
  `pytool.lang.Namespace` objects. This means you can assign descriptor
  instances to Namespace instances, and their values can be read, but not set.

  This differs from normal python descriptor behavior, where the descriptor
  instance must be present in the class rather than the instance.

### 2.3.0

- Make `pytool.lang.Namespace` instances evaluate as `False` when empty and
  cast as a `bool()`.

### 2.2.0

- Added `pytool.proxy.DictProxy` and `pytool.proxy.ListProxy`.

### 2.1.0

- Added `pytool.lang.hashed_singleton`.

### 2.0.1

- Update setup.py to include classifiers.

### 2.0.0

- Add `pytool.time.floor_minute` and `pytool.time.floor_week`.
- Change `pytool.time.floor_month` and `pytool.time.floor_day` to preserve
  timezone information.

### Pre-2.0.0

Sorry, I was lazy and didn't keep a Changelog until 2.0. Apologies!

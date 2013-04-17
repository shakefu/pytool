Changelog
=========

Here you'll find a record of the changes in each version of :mod:`pytool`.

3.0.1
-----

- Fix bug with setup.py which broke installs.

3.0.0
-----

- Changed to depend on simplejson (``>=3.2.0``) for the ``_asdict()`` and
  ``for_json()`` hooks. This may break backwards compatability.

2.4.1
-----

- Fix bug where ``for_json()`` hook was ignored on classes that subclass the
  basic types.
- Fix bug where :func:`pytool.json.as_json` would leave a trailing space on
  timestamps if there is no timezone associated with them.

2.4.0
-----

- Improve documentation.
- Add ``for_json()`` hook in :func:`pytool.json.as_json`.
- Add ``__repr__()`` to :class:`pytool.time.UTC` to make it prettier.
- Add support for ``_asdict()`` hook (implemented by :class:`namedtuple`) even
  when not using :mod:`simplejson`.
- Fix :func:`pytool.time.is_dst` test.
- Add ``for_json()`` hook to :class:`pytool.proxy.DictProxy` and
  :class:`pytool.proxy.ListProxy`.

2.3.2
-----

- Fix descriptor protocol in iteritems.


2.3.1
-----

- Implement a instance-descriptor read-only protocol for
  :class:`pytool.lang.Namespace` objects. This means you can assign descriptor
  instances to Namespace instances, and their values can be read, but not set. 

  This differs from normal python descriptor behavior, where the descriptor
  instance must be present in the class rather than the instance.

2.3.0
-----

- Make :class:`pytool.lang.Namespace` instances evaluate as ``False`` when
  empty and cast as a ``bool()``.

2.2.0
-----

- Added :class:`pytool.proxy.DictProxy` and :class:`pytool.proxy.ListProxy`.

2.1.0
-----

- Added :class:`pytool.lang.hashed_singleton`.

2.0.1
-----

- Update setup.py to include classifiers.

2.0.0
-----

- Add :func:`pytool.time.floor_minute` and :func:`pytool.time.floor_week`.
- Change :func:`pytool.time.floor_month` and :func:`pytool.time.floor_day` to
  preserve timezone information.


Pre-2.0.0
---------

Sorry, I was lazy and didn't keep a Changelog until 2.0. Apologies!


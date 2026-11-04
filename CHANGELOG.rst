*********
Changelog
*********

This project follows the guidelines of `Keep a changelog`_ and adheres to
`Semantic versioning`_.

.. _Keep a changelog: http://keepachangelog.com/
.. _Semantic versioning: https://semver.org/


`0.3.0`_ - 2026-11-04
=====================

Changed
-------
* **Breaking:** Change init argument ``resource`` to only accept full visa
  resource names. Use the new keyword argument ``serial_number`` to initialize
  a generator by its serial number.

Fixed
-----
* Prevent device detection from failing if there are resource names which do
  not match the previously assumed scheme of more than three parts divided by
  ``::``.
* Add numpy to test requirements


`0.2.0`_ - 2026-05-16
=====================

Changed
-------
* Switch to pyproject.toml.


`0.1.0`_ - 2022-12-01
=====================

Added
-----
* First preview release.


.. _0.1.0: https://github.com/emtpb/tektronixsg/releases/tag/0.1.0
.. _0.2.0: https://github.com/emtpb/tektronixsg/releases/tag/0.2.0
.. _0.3.0: https://github.com/emtpb/tektronixsg/releases/tag/0.3.0

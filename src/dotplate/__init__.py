"""
Yet another dotfile manager/templater

``dotplate`` is yet another dotfile manager/templater program and Python
library, written because I couldn't find one that already had the exact
features I wanted.

Features
========

- Dotfiles are defined via Jinja_ templates, which are rendered and written to
  either your home directory or another directory of your choice.

- The templates are stored in a source directory with the same layout as the
  installed dotfiles; e.g., a template at ``.config/foo/bar.toml`` in the
  source directory will, when everything is installed in your home, end up
  rendered & written to ``~/.config/foo/bar.toml``.

- Files in the destination directory that do not correspond to a template are
  ignored.

- Templates are automatically discovered by traversing the source directory.
  If the directory is tracked by Git, only committed files are recognized.

- If a template has the executable bit set, the installed file will have the
  executable bit set.

- Templates can belong to one or more *suites*, groups of files that can be
  enabled & disabled together.  A template in a suite will only be installed if
  one of its suites is enabled on the command line.

- The Jinja templates have access to a ``dotplate`` context variable containing
  information about the local host and optional user-defined values.

- Host-specific configuration (including setting custom values in the
  ``dotplate`` context variable and enabling/disabling suites) can be read from
  a file in a location of your choice.

- Python library API

- Not actually limited to dotfiles; can be used to template any tree of files

.. _Jinja: https://jinja.palletsprojects.com

Visit <https://github.com/jwodder/dotplate> or <https://dotplate.rtfd.io> for
more information.
"""

__version__ = "0.1.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "dotplate@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/dotplate"

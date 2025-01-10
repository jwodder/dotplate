|repostatus| |ci-status| |coverage| |license|

.. |repostatus| image:: https://www.repostatus.org/badges/latest/wip.svg
    :target: https://www.repostatus.org/#wip
    :alt: Project Status: WIP — Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. |ci-status| image:: https://github.com/jwodder/dotplate/actions/workflows/test.yml/badge.svg
    :target: https://github.com/jwodder/dotplate/actions/workflows/test.yml
    :alt: CI Status

.. |coverage| image:: https://codecov.io/gh/jwodder/dotplate/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/dotplate

.. |license| image:: https://img.shields.io/github/license/jwodder/dotplate.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/dotplate>`_
| `Documentation <https://dotplate.readthedocs.io>`_
| `Issues <https://github.com/jwodder/dotplate/issues>`_

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


Installation
============
``dotplate`` requires Python 3.10 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install it::

    python3 -m pip install git+https://github.com/jwodder/dotplate

..
    python3 -m pip install dotplate


Getting Started
===============

To get started using ``dotplate``, create a `TOML <https://toml.io>`_
configuration file named ``dotplate.toml`` following this example:

.. code:: toml

    # The [core] table contains fundamental dotplate configuration.
    [core]

    # Path to the directory of template files, relative to the directory containing
    # `dotplate.toml`.  Defaults to the current directory if not set.
    #
    # It's recommended that you either set this to "." (the current directory, if
    # your templates are in the same directory as the config file) or else put your
    # templates in a directory next to the config file and set `src` to the name of
    # that directory.
    src = "."

    # (Required) Path to the directory where the rendered templates will be
    # installed.  A leading tilde (~) will be replaced with the path to your home
    # directory.
    #
    # This value can be overridden by the local config file or by the `--dest`
    # command-line option.
    dest = "~"

    # Path to an optional secondary configuration file containing settings specific
    # to the host that dotplate is run on.  If not set, no local config is read.
    local-config = "~/.config/dotplate/local.toml"


    # The [jinja] table contains configuration for the Jinja environment used to
    # render the templates.  Most `jinja2.Environment` constructor arguments are
    # supported; see the dotplate documentation for a full list.
    [jinja]

    # Here are some Jinja settings, set to their default values.  You may want to
    # change these settings in particular if they clash with the syntax of the
    # files you're templating.
    block-start-string = "{%"
    block-end-string = "%}"
    variable-start-string = "{{"
    variable-end-string = "}}"


    # Suites are defined by [suite.SUITENAME] tables, like so:
    [suites.my-suite]

    # A list of templates files (relative to the src directory) that belong to this
    # suite.  A template may belong to zero or more suites.  If a template belongs
    # to one or more suites, it will only be installed if one or more of those
    # suites are enabled.
    files = [
        ".config/mine/mine.cfg",
        "bin/do-stuff",
    ]

    # Whether to enable the suite by default.  If not set, the suite is not
    # enabled.
    enabled = true


    # The [vars] table contains custom variables to include in the `dotplate`
    # context variable provided to templates.  The variables set here can be
    # overwritten & augmented by the [vars] table in the host-specific local
    # configuration file, if any.
    [vars]

    # Now you can write `{{ dotplate.vars.editor }}` in templates, and it will
    # be replaced by the string "vim" — unless you've set a different value in
    # the local config.
    editor = "vim"

    additional_paths = [
        "$HOME/local/bin",
        "$HOME/.cargo/bin",
    ]

Now you're ready to begin writing templates.  Let's create a template for a
simple ``~/.profile`` file: Create a file also named ``.profile``, and put it
in the directory indicated by the value you used for ``core.src`` in
``dotplate.toml``.  The following contents for the file make use of the
``vars.editor`` and ``vars.additional_paths`` fields defined in the
configuration file shown above.

.. code:: bash

    export PATH="$PATH:{{ dotplate.vars.additional_paths|join(":") }}"
    export EDITOR={{ dotplate.vars.editor }}

Now, if you run ``dotplate install`` in the directory where the
``dotplate.toml`` file is located, the ``.profile`` file in your home directory
will be replaced by the rendered contents of the template (Don't worry, the
original is backed up at ``~/.profile.dotplate.bak``).  With the `[vars]` table
from the configuration file above, your ``~/.profile`` will now contain:

.. code:: bash

    export PATH="$PATH:$HOME/local/bin:$HOME/.cargo/bin"
    export EDITOR=vim

See `the dotplate documentation <Documentation_>`_ for more information.

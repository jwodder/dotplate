`dotplate` — A dotfile installer/manager/templater with the features that I
want

- Features:
    - Source files are Jinja template files in a source directory
    - Source files are templated & installed (copied/written out) to paths in a
      destination directory
        - Executable bits on files are preserved
        - Files that would be overwritten are backed up
    - A file's destination path relative to `dest` is the same as its path
      relative to `src`
    - By default, all files in the source tree are installed
    - Source files can belong to one or more suites, in which case they are
      installed iff one or more of those suites is enabled on the command line
    - If the source tree is in a Git directory, ignored & untracked files are ignored
    - The Jinja templates are passed info about the host, suites, etc.
    - machine-specific config files supported
    - Files in the destination tree that do not exist in the source tree are
      ignored
    - usable as a Python library

- s/suite/feature/?

- Come up with a better name for "src paths"

- Other possible features:
    - Support running scripts to generate config to augment/take the place of
      the machine-specific config
    - Post-install actions?
    - Support deleting files from `dest` that are only in disabled suites?
    - Support omitting files that render to emptiness/whitespace?
    - Selecting suites automatically based on OS details?
    - Jinja templates in `[vars]` values?
    - Support binary files?
    - Support disabling auto-installation of everything by default?
    - Marking files & directories as only user-accessible (i.e., unmask group &
      "other" mode bits)
    - configurable backup extension?
    - Reporting files that exist in dest directories but not in src?

- Possible names:
    - `dotplate`
    - `dtf`
    - `dotdotdot` (taken)
    - `ddd` (taken)
    - `speck` (taken)
    - `filespeck`
    - `dotspeck`

- Config file:
    - TOML
    - location specified on command line, defaulting to `dotplate.toml` in
      current directory
    - Contents:
        - `[paths]`
            - `src` — path to directory containing source files/templates to
              install
                - relative to directory containing config file
                - defaults to directory containing config file (in which case
                  config file is not counted as part of its contents)
            - `dest` — path where managed files are installed
                - can be set on command line
                - can be set in local config file
                - default to `$HOME`?
            - `local-config` — path to config file for local machine
                - can be set on command line
                - If not set, not used
        - `[jinja]` — Jinja config
        - `[suites.NAME]`
            - `files: list[str]` — list of src paths of files in the suite
            - `enabled: bool = False` — whether the suite is enabled by default
        - `[vars]` — extra variables usable in templates
            - can be extended via local config
            - support extension via command line?

- Local config file (TOML):
    - `enabled-suites` — list of suite names
    - `dest`
    - `[vars]` — overwrites corresponding keys in `[vars]` in main config file

- CLI options:
    - `-s`/`--enable-suite <name>` (multiple-use)
    - `-S`/`--disable-suite <name>` (multiple-use)
    - `--no-default-suites`?
    - config file location
    - local config file location
    - `dest` path

- Subcommands:
    - `install [src-path ...]`
        - `src-path` is relative to `src` (and also `dest`)
        - Installs everything if no `src-path` given
        - `src-path` can be a directory to install everything therein
        - has options for whether to create backups of replaced files
        - Unless a `--yes` option is given, for each file that would be
          installed, you are asked whether you want to install it, and you have
          the option to view a diff at this time
    - `list` — list all paths that would be installed
    - `render <src-path>` — print templated content of file
    - `diff [src-path ...]`
        - Diffs everything if no `src-path` given
        - Have a short mode that just lists all files and whether they differ?
            - Add an option for only listing files that differ
    - [dump Jinja context var?]

- The Jinja templates have access to a `dotplate` object with the following
  attributes:
    - `host` — info about the host machine
        - `os` — equals `os.name`
        - `hostname`
        - `arch`?
        - stuff from `distro`?
        - stuff from `platform`?
    - `suites`
        - `enabled`: `list[str]`
        - `files` — map from suite names to their src paths
    - `dest` — absolutized path
    - `vars` — extra variables defined in config file

- Also give the Jinja templates access to a `which()` function that returns
  none/undefined when the program is not found?
    - Allow the function to take multiple arguments, in which case it falls
      back to the next program when the current one is not found?

- Library API:
    - `GlobalConfig.from_file(Path)` (or just `Config`?)
        - also constructible manually (or via pydantic?)
        - Tildes are expanded by pydantic
        - `resolve_paths_relative_to(p: Path) -> None`
            - Called automatically by `from_file()` method
        - `merge_local_config(cfg: LocalConfig) -> None`
        - `load_local_config() -> None`
            - Reads the local config from disk and merges it in
    - `LocalConfig.from_file(Path)`
        - also constructible manually (or via pydantic?)
        - Tildes are expanded by pydantic
        - `resolve_paths_relative_to(p: Path) -> None`
            - Called automatically by `from_file()` method
    - `Dotplate.from_config(cfg: GlobalConfig)`
    - `Dotplate`:
        - `enable_suite(suite: str)`
        - `disable_suite(suite: str)`
        - `src_paths() -> list[str]`
        - `render(src_path: str) -> RenderedFile`
        - `install(src_paths: list[str] | None) -> None`
        - [get & manipulate the context]
    - `RenderedFile`
        - public: `__init__(content: str, relative_path: Path, dest: Path, executable: bool = False) -> None`
        - `relative_path: Path` — path relative to base of src
        - `dest: Path`
        - `executable: bool = False`
        - `install(dest: Path | None) -> None`
        - `install_in_dir(dir: Path) -> None`
        - `diff(dest: Path | None) -> str`
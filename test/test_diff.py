from conftest import CaseDirs
@pytest.mark.usecase("simple")
def test_simple_nodiff(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    shutil.copyfile(casedirs.dest / ".profile", tmp_home / ".profile")
@pytest.mark.usecase("simple")
def test_simple_changed(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
@pytest.mark.usecase("simple")
def test_simple_missing(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
@pytest.mark.usecase("simple")
def test_simple_xbit_added(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    shutil.copyfile(casedirs.dest / ".profile", tmp_home / ".profile")
@pytest.mark.usecase("simple")
def test_simple_changed_xbit_added(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
@pytest.mark.usecase("script")
def test_script_nodiff(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
        casedirs.dest / "bin" / "flavoring",
@pytest.mark.usecase("script")
def test_script_xbit_removed(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
        casedirs.dest / "bin" / "flavoring",
@pytest.mark.usecase("script")
def test_script_changed_xbit_removed(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
@pytest.mark.usecase("script")
def test_script_missing(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
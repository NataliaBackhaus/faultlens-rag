from packaging.version import Version

from ingest.aliases import _normalize, firmware_in_range, load_aliases, parse_version, resolve

ALIASES = load_aliases()


# --- _normalize ---


def test_normalize_lowercase():
    assert _normalize("SB 2500HF") == "sb2500hf"


def test_normalize_removes_hyphens():
    assert _normalize("SB-2500HF") == "sb2500hf"


def test_normalize_removes_dots():
    assert _normalize("Symo 10.0") == "symo100"


def test_normalize_variants_are_equal():
    assert _normalize("SB 2500HF") == _normalize("SB-2500HF") == _normalize("SB2500HF")


# --- resolve ---


def test_resolve_exact_match():
    assert resolve("SB 2500HF", ALIASES) == "sma_sunnyboy_hf_2-3kw"


def test_resolve_case_insensitive():
    assert resolve("sb 2500hf", ALIASES) == "sma_sunnyboy_hf_2-3kw"


def test_resolve_full_name():
    assert resolve("Sunny Boy 2500HF", ALIASES) == "sma_sunnyboy_hf_2-3kw"


def test_resolve_with_suffix():
    assert resolve("SB 2500HF-30", ALIASES) == "sma_sunnyboy_hf_2-3kw"


def test_resolve_tl_abbreviation():
    assert resolve("SB 5.0", ALIASES) == "sma_sunnyboy_tl_3-5kw"


def test_resolve_sunny_boy_tl_full():
    assert resolve("Sunny Boy 5000TL", ALIASES) == "sma_sunnyboy_tl_3-5kw"


def test_resolve_fronius_symo_full():
    assert resolve("Fronius Symo 10.0-3-M", ALIASES) == "fronius_symo_10-20kw"


def test_resolve_fronius_symo_short():
    assert resolve("Symo 15.0", ALIASES) == "fronius_symo_10-20kw"


def test_resolve_unknown_returns_none():
    assert resolve("unknown model xyz", ALIASES) is None


def test_resolve_empty_string_returns_none():
    assert resolve("", ALIASES) is None


# --- parse_version ---


def test_parse_version_returns_version_object():
    assert isinstance(parse_version("3.0.5"), Version)


def test_parse_version_comparison():
    assert parse_version("10.0") > parse_version("9.0")


def test_parse_version_equal():
    assert parse_version("3.0") == parse_version("3.0.0")


# --- firmware_in_range ---


def test_firmware_in_range_none_accepts_all():
    assert firmware_in_range("3.2.1", None) is True


def test_firmware_in_range_within():
    assert firmware_in_range("3.2.1", ">=3.0,<4.0") is True


def test_firmware_in_range_below():
    assert firmware_in_range("2.9.0", ">=3.0,<4.0") is False


def test_firmware_in_range_above():
    assert firmware_in_range("4.1.0", ">=3.0,<4.0") is False


def test_firmware_in_range_exact_lower_bound():
    assert firmware_in_range("3.0.0", ">=3.0,<4.0") is True


def test_firmware_in_range_exact_upper_bound_excluded():
    assert firmware_in_range("4.0.0", ">=3.0,<4.0") is False

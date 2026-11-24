"""Tests for typing_guide_examples.py, the runnable companion to the typing guide.

Three kinds of claim are checked:

1. Runtime behaviour: what each example does when executed.
2. Static behaviour: the module passes ``mypy --strict``, and every line the
   guide says a checker rejects really is rejected (and nothing else is).
3. Synchronisation: every Python block in the guide is an excerpt of the
   tested module.

Run with:  pytest -q
Requires:  pytest, mypy, pydantic.
The guide is looked up next to this file (type_hinting_git_v*.md) or at
$TYPING_GUIDE_PATH; the synchronisation test is skipped if it is absent.
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import get_args

import pytest

import typing_guide_examples as ex

HERE = Path(__file__).resolve().parent
EXAMPLES_PATH = HERE / "typing_guide_examples.py"
_GUIDES = sorted(HERE.glob("type_hinting_git_v*.md"))
GUIDE_PATH = Path(os.environ.get("TYPING_GUIDE_PATH", _GUIDES[-1] if _GUIDES else HERE / "type_hinting_git.md"))
MYPY_TARGET = "3.14"

SNIPPET_START = re.compile(r"^\s*# \[snippet: ([\w-]+)\]\s*$")
SNIPPET_END = re.compile(r"^\s*# \[end\]\s*$")
REJECTED_LINE = re.compile(r"^(\s*)#! (.*)$")


# --------------------------------------------------------------------------- helpers

def extract_snippets(source: str) -> dict[str, str]:
    """Return {snippet id: text} exactly as the guide shows it.

    Regions sharing an id are concatenated in file order. Each region is
    dedented, and '#! ' (checker-rejected code) becomes an ordinary comment.
    """
    regions: dict[str, list[str]] = {}
    current: str | None = None
    buffer: list[str] = []
    for line in source.splitlines():
        start = SNIPPET_START.match(line)
        if start:
            assert current is None, f"nested snippet at {line!r}"
            current, buffer = start.group(1), []
        elif SNIPPET_END.match(line):
            assert current is not None, "'# [end]' without a snippet start"
            text = textwrap.dedent("\n".join(buffer)).strip("\n")
            text = re.sub(r"^(\s*)#! ", r"\1# ", text, flags=re.MULTILINE)
            regions.setdefault(current, []).append(text)
            current = None
        elif current is not None:
            buffer.append(line.rstrip())
    assert current is None, f"snippet {current!r} never ended"
    return {name: "\n\n".join(parts) for name, parts in regions.items()}


def guide_python_blocks(markdown: str) -> list[tuple[int, str]]:
    """Return (line number, dedented code) for every ```python block in the guide."""
    blocks: list[tuple[int, str]] = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        if re.match(r"^\s*```python\s*$", lines[i]):
            start = i + 1
            j = start
            while not re.match(r"^\s*```\s*$", lines[j]):
                j += 1
            blocks.append((start, textwrap.dedent("\n".join(lines[start:j])).strip("\n")))
            i = j
        i += 1
    return blocks


def run_mypy(path: Path) -> dict[int, list[str]]:
    """Run mypy --strict on one file; return {line number: [error messages]}."""
    proc = subprocess.run(
        [
            sys.executable, "-m", "mypy", "--strict", "--python-version", MYPY_TARGET,
            "--no-error-summary", "--no-pretty", "--show-error-codes",
            "--cache-dir", os.devnull, str(path),
        ],
        capture_output=True, text=True, cwd=path.parent,
    )
    errors: dict[int, list[str]] = {}
    for line in proc.stdout.splitlines():
        found = re.match(r"^[^:]+:(\d+): error: (.*)$", line)
        if found:
            errors.setdefault(int(found.group(1)), []).append(found.group(2))
    assert errors or proc.returncode == 0, proc.stdout + proc.stderr
    return errors


def mypy_reveal(tmp_path: Path, body: str) -> list[str]:
    """Type-check a small source text; return the revealed types and any errors."""
    path = tmp_path / "probe.py"
    path.write_text(textwrap.dedent(body))
    proc = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", "--python-version", MYPY_TARGET,
         "--no-error-summary", "--cache-dir", os.devnull, str(path)],
        capture_output=True, text=True, cwd=tmp_path,
    )
    return [line.split(": ", 2)[-1] for line in proc.stdout.splitlines()]


def output_of(capsys: pytest.CaptureFixture[str], demo) -> list[str]:
    demo()
    return capsys.readouterr().out.splitlines()


# --------------------------------------------------------------------------- static checks

def test_module_passes_mypy_strict():
    assert run_mypy(EXAMPLES_PATH) == {}


def test_checker_rejects_exactly_the_lines_the_guide_says_it_rejects(tmp_path):
    """Uncomment every '#! ' line; mypy must flag each '# ERROR' line and nothing else."""
    expected: set[int] = set()
    variant: list[str] = []
    for number, line in enumerate(EXAMPLES_PATH.read_text().splitlines(), start=1):
        rejected = REJECTED_LINE.match(line)
        if rejected:
            line = rejected.group(1) + rejected.group(2)
            if "# ERROR" in line:
                expected.add(number)
        else:
            assert "# ERROR" not in line, f"line {number}: '# ERROR' outside a '#! ' line"
        variant.append(line)
    assert len(expected) >= 30, "expected-error markers went missing"

    path = tmp_path / "rejected_variant.py"
    path.write_text("\n".join(variant) + "\n")
    errors = run_mypy(path)

    not_flagged = sorted(expected - errors.keys())
    unexpected = {n: errors[n] for n in sorted(errors.keys() - expected)}
    assert not not_flagged, f"mypy accepted lines the guide says are errors: {not_flagged}"
    assert not unexpected, f"mypy reported errors on unmarked lines: {unexpected}"


def test_mypy_specific_inference_claims(tmp_path):
    out = mypy_reveal(tmp_path, """
        from typing import NotRequired, TypedDict, reveal_type

        def f(is_text: bool) -> None:
            data = "some text" if is_text else b"some_bytes"
            reveal_type(data)
            mixed_data = [42, "answer", 6.022e23]
            reveal_type(mixed_data)

        class ShipHistoryData(TypedDict):
            name: str
            commission_date: NotRequired[int]

        def g(data: ShipHistoryData) -> int:
            return data["commission_date"]  # mypy does not flag this access
    """)
    assert out == ['Revealed type is "str | bytes"', 'Revealed type is "list[object]"']


def test_alias_made_with_type_statement_is_transparent_to_the_checker(tmp_path):
    """The reason the guide uses NewType for domain distinctions."""
    out = mypy_reveal(tmp_path, """
        type USD = int
        type GBP = int

        def pay_usd(amount: USD) -> None: ...

        pounds: GBP = 5
        pay_usd(pounds)
        pay_usd(5)
    """)
    assert out == []


def test_collections_abc_is_protocol_based_in_the_stubs_but_not_at_runtime(tmp_path):
    import collections.abc
    import typing

    # Runtime: a plain ABC; Protocol is not among its bases.
    assert typing.Protocol not in collections.abc.Iterable.__mro__
    assert type(collections.abc.Iterable).__name__ == "ABCMeta"
    # @runtime_checkable only works on Protocol classes.
    with pytest.raises(TypeError, match="protocol"):
        typing.runtime_checkable(int)

    # Static: the checker accepts a structural match for Iterable (a protocol in
    # the stubs) and rejects one for Sequence (a nominal class there).
    out = mypy_reveal(tmp_path, """
        from collections.abc import Iterable, Iterator, Sequence

        class Deck:
            def __iter__(self) -> Iterator[int]: return iter([1])
            def __len__(self) -> int: return 1
            def __getitem__(self, index: int) -> int: return 1

        a: Iterable[int] = Deck()
        b: Sequence[int] = Deck()
    """)
    assert len(out) == 1 and "Sequence[int]" in out[0]


# --------------------------------------------------------------------------- guide sync

def test_snippet_markers_are_well_formed():
    snippets = extract_snippets(EXAMPLES_PATH.read_text())
    assert len(snippets) >= 50
    assert all(text.strip() for text in snippets.values())
    assert not any("#!" in text for text in snippets.values())


@pytest.mark.skipif(not GUIDE_PATH.exists(), reason=f"guide not found at {GUIDE_PATH}")
def test_every_python_block_in_the_guide_comes_from_the_tested_module():
    snippet_lines = [
        [line.rstrip() for line in text.splitlines()]
        for text in extract_snippets(EXAMPLES_PATH.read_text()).values()
    ]

    def is_excerpt(block: str) -> bool:
        wanted = [line.rstrip() for line in block.splitlines()]
        return any(
            lines[i:i + len(wanted)] == wanted
            for lines in snippet_lines
            for i in range(len(lines) - len(wanted) + 1)
        )

    blocks = guide_python_blocks(GUIDE_PATH.read_text())
    assert len(blocks) >= 55
    stale = [line for line, block in blocks if not is_excerpt(block)]
    assert not stale, f"guide blocks (by line) that are not excerpts of the module: {stale}"


# --------------------------------------------------------------------------- runtime: whole module

def test_every_demo_runs(capsys):
    ex.main()
    out = capsys.readouterr().out
    assert out.count("=== demo_") >= 35


def test_importing_the_module_prints_nothing():
    proc = subprocess.run(
        [sys.executable, "-c", "import typing_guide_examples"],
        capture_output=True, text=True, cwd=HERE,
    )
    assert (proc.returncode, proc.stdout, proc.stderr) == (0, "", "")


# --------------------------------------------------------------------------- runtime: basics

def test_core_annotations(capsys):
    assert output_of(capsys, ex.demo_core_annotations) == [
        "1014 crew assigned to the USS Enterprise-D.",
        "USS Enterprise-D: Nominal.",
    ]


def test_builtin_generics(capsys):
    assert output_of(capsys, ex.demo_builtin_generics) == ["Picard: 9", "Q: N/A", "Riker: 8"]


def test_annotations_are_not_enforced_at_runtime(capsys):
    # Literal["standby", "engage", "emergency"] is a static constraint only.
    ex.set_warp_drive_mode("full_speed")  # type: ignore[arg-type]
    assert capsys.readouterr().out == "Warp drive mode set to: full_speed\n"


def test_any_defers_the_failure_to_runtime(capsys):
    ex.process_any("engage")
    assert capsys.readouterr().out == "Processing any: ENGAGE\n"
    with pytest.raises(AttributeError):
        ex.process_any(1701)


def test_object_requires_narrowing(capsys):
    assert output_of(capsys, ex.demo_any_vs_object) == [
        "Processing any: ENGAGE",
        "Processing object as string: ENGAGE",
    ]


@pytest.mark.skipif(sys.version_info < (3, 14), reason="deferred annotations need Python 3.14")
def test_forward_references_work_unquoted_on_314():
    ex.demo_forward_references()
    assert set(ex.Flagship.__annotations__) == {"commander"}


@pytest.mark.skipif(sys.version_info >= (3, 14), reason="only fails before Python 3.14")
def test_unquoted_forward_reference_fails_before_314():
    source = extract_snippets(EXAMPLES_PATH.read_text())["forward-references"]
    with pytest.raises(NameError, match="Captain"):
        exec(source, {})


def test_type_aliases(capsys):
    assert output_of(capsys, ex.demo_type_aliases) == [
        "Manifest for Galaxy-class:",
        "  - ID: 1, Name: Picard",
        "  - ID: 2, Name: Riker",
        "2 True",
    ]


def test_generic_alias(capsys):
    assert output_of(capsys, ex.demo_generic_alias) == ["[202, 303] ['riker', 'worf']"]
    assert output_of(capsys, ex.demo_generic_alias_legacy) == ["[202]"]


def test_newtype_is_distinct_statically_and_free_at_runtime(capsys):
    assert output_of(capsys, ex.demo_newtype) == [
        "Posted 1999 cents", "Posted 1999 cents", "Posted 1999 cents",
    ]
    raw = ex.USDCentsRaw(250)
    assert type(raw) is int
    assert type(ex.validate_cents(raw)) is int
    with pytest.raises(ValueError):
        ex.validate_cents(ex.USDCentsRaw(-1))


def test_tuples(capsys):
    assert output_of(capsys, ex.demo_tuple_record) == ["USS Enterprise (Galaxy): Active"]
    assert output_of(capsys, ex.demo_tuple_variadic) == ["1701", "(1701,) ()"]


# --------------------------------------------------------------------------- runtime: narrowing

def test_inference_demos(capsys):
    assert output_of(capsys, ex.demo_common_type) == ["str 3 3"]
    assert output_of(capsys, ex.demo_numeric) == ["15.5 9 True"]


def test_conditional_resolution(capsys):
    assert output_of(capsys, ex.demo_conditional_resolution) == ["NCC-1701", "1701", "6 0 0", "RIKER"]


def test_assert_narrowing_raises_when_assertions_are_enabled():
    with pytest.raises(AssertionError, match="UID must be a string"):
        ex.must_be_string(5)


def test_assert_narrowing_is_not_a_check_under_dash_O():
    """python -O strips assert statements, so the 'proof' vanishes."""
    proc = subprocess.run(
        [sys.executable, "-O", "-c", "import typing_guide_examples as e; e.must_be_string(5)"],
        capture_output=True, text=True, cwd=HERE,
    )
    assert proc.returncode != 0
    assert "AttributeError" in proc.stderr and "AssertionError" not in proc.stderr


def test_typeis(capsys):
    assert output_of(capsys, ex.demo_typeis) == [
        "Logging Officer Roster:",
        "- Commander Picard",
        "- Commander Riker",
        "- Commander Data",
        "Manifest contains invalid data; cannot log roster.",
    ]
    assert ex.is_officer_manifest([]) is True


def test_match(capsys):
    assert ex.process_command(ex.EngageCommand(9.1)) == 9.1
    assert ex.process_command(ex.ReportStatusCommand("shields")) == "Report for shields: All systems nominal."
    assert ex.process_command(ex.SetAlertCommand("red")) is None
    assert ex.process_command(ex.SetAlertCommand("red", "Borg")) is None
    assert capsys.readouterr().out.splitlines() == [
        "Executing: Engage warp drive at speed 9.1.",
        "Report for shields: All systems nominal.",
        "Executing: Setting alert to RED.",
        "Executing: Setting alert to RED (Borg).",
    ]


def test_match_assert_never_fires_on_an_unhandled_value():
    with pytest.raises(AssertionError):
        ex.process_command("not a command")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- runtime: promises vs. proof

def test_get_args_needs_the_alias_value():
    """Regression: get_args() on a 'type' alias returns (), so the guard always failed."""
    assert get_args(ex.ShipIdKey) == ()
    assert get_args(ex.ShipIdKey.__value__) == ("name", "registry")
    assert ex.is_ship_id_key("name") and ex.is_ship_id_key("registry")
    assert not ex.is_ship_id_key("captain")


def test_guard_accepts_valid_keys_and_rejects_invalid_ones(capsys):
    ship = ex.ShipIdCard(name="Voyager", registry="NCC-74656")
    ex.update_with_guard(ship, "name", "Enterprise")
    assert ship["name"] == "Enterprise"
    assert capsys.readouterr().out == ""
    ex.update_with_guard(ship, "captain", "Janeway")
    assert capsys.readouterr().out == "'captain' is not a valid key.\n"
    assert "captain" not in ship


def test_cast_with_an_invalid_key_raises_nothing_and_corrupts_the_dict():
    """Regression: the guide used to claim this raises KeyError."""
    ship = ex.ShipIdCard(name="Voyager", registry="NCC-74656")
    ex.update_with_cast(ship, "captain", "Janeway")
    assert dict(ship) == {"name": "Voyager", "registry": "NCC-74656", "captain": "Janeway"}


def test_guard_vs_cast_demo(capsys):
    assert output_of(capsys, ex.demo_guard_vs_cast) == [
        "'captain' is not a valid key.",
        "['captain', 'name', 'registry']",
    ]


# --------------------------------------------------------------------------- runtime: the edge

def test_typeddict_demo(capsys):
    assert output_of(capsys, ex.demo_typeddict_edge) == [
        "Registering NCC-1701-D: USS Enterprise",
        "Crew complement: 1014",
    ]


def test_typeddict_annotation_is_an_unchecked_promise():
    ship: ex.StarshipData = json.loads('{"name": 7}')  # accepted statically and at runtime
    assert type(ship) is dict
    with pytest.raises(KeyError):
        ex.register_ship(ship)


def test_typeddict_optional_keys(capsys):
    assert output_of(capsys, ex.demo_typeddict_optional_keys) == [
        "Processing USS Enterprise (NCC-1701-D)",
        "Commissioned in 2363",
        "Processing USS Pegasus (NCC-53847)",
        "Commissioned in 2371",
    ]


VALID_SHIP = {"name": "USS Enterprise", "registry": "NCC-1701-D", "crew_count": 1014, "is_commissioned": True}


def test_from_dict_builds_a_record(capsys):
    record = ex.StarshipRecord.from_dict(VALID_SHIP)
    assert record == ex.StarshipRecord("USS Enterprise", "NCC-1701-D", 1014, True)
    assert output_of(capsys, ex.demo_dataclass_boundary) == ["USS Enterprise (NCC-1701-D) - Status: Active"]


@pytest.mark.parametrize(
    ("change", "error"),
    [
        ({"name": 1701}, TypeError),
        ({"registry": None}, TypeError),
        ({"crew_count": "one thousand and fourteen"}, TypeError),
        ({"crew_count": 1014.0}, TypeError),
        ({"crew_count": True}, TypeError),
        ({"crew_count": -1}, ValueError),
        ({"is_commissioned": "yes"}, TypeError),
        ({"is_commissioned": 1}, TypeError),
    ],
)
def test_from_dict_rejects_invalid_values(change, error):
    """Regression: from_dict used to accept all of these."""
    with pytest.raises(error):
        ex.StarshipRecord.from_dict({**VALID_SHIP, **change})


@pytest.mark.parametrize("missing", sorted(VALID_SHIP))
def test_from_dict_rejects_missing_keys(missing):
    data = {key: value for key, value in VALID_SHIP.items() if key != missing}
    with pytest.raises(KeyError):
        ex.StarshipRecord.from_dict(data)


def test_plain_dataclass_construction_validates_nothing():
    """Why from_dict has to do the checking: the dataclass constructor does not."""
    record = ex.StarshipRecord(name=1, registry=None, crew_count="many", is_commissioned="maybe")  # type: ignore[arg-type]
    assert record.crew_count == "many"


# --------------------------------------------------------------------------- runtime: functions

def test_sync_functions(capsys):
    assert output_of(capsys, ex.demo_sync_functions) == ["42", "WARP 9", "IRW Khazara: Cloaked."]


def test_never_function_raises():
    with pytest.raises(ValueError, match="boom"):
        ex.fail_with_error("boom")
    with pytest.raises(ValueError, match="Unexpected type"):
        ex.stringify(9.5)  # type: ignore[arg-type]


def test_self_preserves_the_subclass(capsys):
    assert output_of(capsys, ex.demo_self_type) == ["Battlecruiser 9 True"]


def test_calling_an_async_function_runs_none_of_its_body():
    ran: list[str] = []

    async def fetch() -> str:
        ran.append("body")
        return "done"

    coro = fetch()
    assert ran == []  # nothing has executed; no event loop is involved yet
    assert asyncio.run(coro) == "done"
    assert ran == ["body"]


def test_async_demo(capsys):
    assert output_of(capsys, ex.demo_async) == [
        "LOG: STATUS FOR NCC-1701-D: ALL SYSTEMS NOMINAL.",
        "LOG: STATUS FOR NCC-74656: ALL SYSTEMS NOMINAL.",
    ]


def test_coroutine_and_generator_annotations_differ(capsys):
    assert output_of(capsys, ex.demo_coroutine_vs_generator) == ["[1, 2, 3] all decks reported"]
    generator = ex.count_decks(1)
    assert next(generator) == 1
    with pytest.raises(StopIteration) as stop:
        next(generator)
    assert stop.value.value == "all decks reported"


# --------------------------------------------------------------------------- runtime: generics

def test_generic_function(capsys):
    assert output_of(capsys, ex.demo_generic_function) == ["Worf 1701"]
    with pytest.raises(ValueError):
        ex.get_first_element([])


def test_typevar_bound(capsys):
    assert output_of(capsys, ex.demo_typevar_bound) == [
        "- IRW Khazara: Cloaked.", "- IRW Belak: Cloaked.", "IRW Khazara",
    ]


def test_variance(capsys):
    assert output_of(capsys, ex.demo_invariance) == ["1"]
    assert output_of(capsys, ex.demo_variance) == [
        "Latest entry: IRW Khazara: Cloaked.",
        "Repair #1 scheduled.",
        "USS Enterprise",
        "IRW Khazara",
        "Archived: IRW Khazara: Cloaked.",
    ]


def test_hof_typevar(capsys):
    assert output_of(capsys, ex.demo_hof_typevar) == ["1014 1701"]


def test_typevartuple(capsys):
    assert ex.apply_operations("USS Enterprise", 1701, True) == ("USS Enterprise", 1701, True)
    assert output_of(capsys, ex.demo_typevartuple) == ["USS Enterprise 1701"]
    assert output_of(capsys, ex.demo_typevartuple_class) == ["1701"]


def test_star_syntax_is_legal_wherever_unpack_is():
    """Regression: the guide used to say Generic[...] requires Unpack[Ts]."""
    namespace: dict[str, object] = {}
    exec(
        "from typing import Generic, TypeVarTuple\n"
        "Ts = TypeVarTuple('Ts')\n"
        "class Old(Generic[*Ts]): ...\n"
        "class New[*Us]: ...\n",
        namespace,
    )
    assert ex.LegacyRecord("Defiant", 74205).get_items() == ex.Record("Defiant", 74205).get_items()


def test_unpack(capsys):
    assert output_of(capsys, ex.demo_unpack) == [
        "('Defiant', 74205)",
        "RED ALERT: Shields down",
        "YELLOW ALERT: no details",
    ]


def test_typevar_constraints(capsys):
    assert output_of(capsys, ex.demo_typevar_constraints) == ["NCC-1701 b'NCC-1701'"]
    assert list(ex.count_decks_as_iterator(2)) == [1, 2]


def test_shared_type_variable_does_not_force_identical_argument_types(tmp_path):
    out = mypy_reveal(tmp_path, """
        from typing import reveal_type

        def same[T](a: T, b: T) -> T:
            return a

        reveal_type(same(1, "a"))
    """)
    assert out == ['Revealed type is "object"']


def test_slots_can_affect_static_checking(tmp_path):
    out = mypy_reveal(tmp_path, """
        from dataclasses import dataclass

        @dataclass(slots=True)
        class Slotted:
            a: int
            def grow(self) -> None:
                self.b = 2
    """)
    assert len(out) == 1 and "__slots__" in out[0]


def test_override_only_sets_an_attribute_at_runtime():
    from typing import override

    class Base:
        def report(self) -> str:
            return "base"

    class Child(Base):
        @override
        def report(self) -> str:
            return "child"

        @override
        def not_in_base(self) -> str:  # a checker rejects this; the runtime does not
            return "accepted at runtime"

    assert Child.report.__override__ is True
    assert Child().not_in_base() == "accepted at runtime"


def test_final_does_not_freeze_the_object():
    assert ex.DECK_NUMBERS == [1, 2, 3]


# --------------------------------------------------------------------------- runtime: decorators

def test_naive_decorator_lets_a_reversed_call_through_to_a_runtime_failure(capsys):
    assert output_of(capsys, ex.demo_naive_decorator) == [
        "Calling function: set_course",
        "Runtime failure: 'int' object has no attribute 'upper'",
        "Calling function: set_course",
        "Setting course for GALAXY at heading 90",
    ]


def test_paramspec_decorator(capsys):
    assert output_of(capsys, ex.demo_paramspec) == [
        "Log: Calling staff_ship_class with arguments ('Galaxy', 1014) and {}",
        "Log: staff_ship_class returned '1014 crew assigned to Galaxy-class starship.'",
        "Log: Calling set_alert_status with arguments () and {'status': 'red'}",
        "Alert status is now red.",
        "Log: set_alert_status returned None",
        "Log: Calling set_alert_status with arguments () and {}",
        "Alert status is now green.",
        "Log: set_alert_status returned None",
        "1014 crew assigned to Galaxy-class starship.",
    ]
    assert ex.staff_ship_class.__name__ == "staff_ship_class"
    assert ex.staff_ship_class.__doc__ == "Assigns crew and returns a confirmation message."


# --------------------------------------------------------------------------- runtime: constraints, protocol, pydantic

def test_literal(capsys):
    assert output_of(capsys, ex.demo_literal) == ["Warp drive mode set to: engage"]


def test_constraints(capsys):
    assert output_of(capsys, ex.demo_constraints) == [
        "9.975",
        "ALERT: RED ALERT",
        "ID-7 Status: Cloaked.",
        "NCC",
        "NCC",
        "USS",
    ]
    assert ex.Runabout.registry_prefix == "NCC"


def test_protocol(capsys):
    assert output_of(capsys, ex.demo_protocol) == [
        "Report for SS Xhosa: Active",
        "Report for Warp Core: Online at 99.8%",
    ]
    assert ex.Reportable not in ex.Freighter.__mro__


def test_pydantic_rejects_bad_data_and_converts_compatible_data(capsys):
    out = output_of(capsys, ex.demo_pydantic)
    assert out[:3] == [
        "Failed to parse starship data. Errors:",
        "1 validation error for StarshipModel",
        "crew_count",
    ]
    assert out[3].startswith(
        "  Input should be a valid integer, unable to parse string as an integer [type=int_parsing,"
    )
    converted = ex.StarshipModel.model_validate({**VALID_SHIP, "crew_count": "1014"})
    assert converted.crew_count == 1014

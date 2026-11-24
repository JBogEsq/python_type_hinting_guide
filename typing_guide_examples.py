"""Runnable companion to "Overview of Python Type Hinting".

Every Python code block in the guide is an excerpt of this module. The regions
between ``# [snippet: <id>]`` and ``# [end]`` are copied into the guide verbatim
(dedented), so the code a reader sees is the code that was executed and
type-checked.

Conventions
-----------
* Lines beginning ``#! `` hold code that a static type checker must REJECT. The
  test suite uncomments each one and confirms that mypy reports an error on
  exactly the lines carrying an ERROR marker and nowhere else. In the guide they
  appear as ordinary comments.
* ``assert_type(value, T)`` is a no-op at runtime; a type checker reports an
  error if the inferred type of ``value`` is not exactly ``T``.
* Usage code lives in ``demo_*`` functions so that importing the module prints
  nothing. ``python typing_guide_examples.py`` runs every demo in guide order.

Validation target: mypy --strict --python-version 3.14. The forward-reference
example needs the Python 3.14 runtime (PEP 649) and is skipped on older ones.
"""

import sys

# =============================================================================
# Syntax Parallels Object Declarations
# =============================================================================

# [snippet: collections-homogeneous]
names: list[str] = ["Picard", "Riker"]
unique_ids: set[int] = {1701, 74656, 75294}
# [end]

# [snippet: collections-heterogeneous]
mixed_list: list[str | int] = ["hello", 42, "world"]  # Any position can be str or int
person_data: tuple[str, int, bool] = ("Picard", 65, True)  # Position 0=str, 1=int, 2=bool
# [end]


# =============================================================================
# The Modern Standard: Built-in Generics
# =============================================================================

# [snippet: builtin-generics]
# The modern, preferred way (Python 3.9+)
def process_data(names: list[str], scores: dict[str, int]) -> None:
    for name in names:
        print(f"{name}: {scores.get(name, 'N/A')}")

# The older, legacy way
from typing import Dict, List

def process_data_legacy(names: List[str], scores: Dict[str, int]) -> None:
    # Functionally identical, but more verbose
    process_data(names, scores)
# [end]


def demo_builtin_generics() -> None:
    process_data(["Picard", "Q"], {"Picard": 9})
    process_data_legacy(["Riker"], {"Riker": 8})


# =============================================================================
# Core Annotation Syntax
# =============================================================================

# [snippet: core-variables]
# Variable annotation
captain: str = "Picard"

class Starship:
    # Class attribute annotation
    registry_prefix: str = "NCC"

    def __init__(self, name: str) -> None:
        # Instance attribute annotation
        self.name: str = name
# [end]

    # [snippet: core-returns]
    # A method on Starship: the return type follows the arrow.
    def get_status_report(self) -> str:
        return f"{self.name}: Nominal."
    # [end]


# [snippet: core-parameters]
# Each parameter is annotated after a colon.
# ('-> None' is the return annotation, covered in the next step.)
def rename_ship(ship: Starship, new_name: str) -> None:
    ship.name = new_name
# [end]


# [snippet: core-returns]
# A function: same syntax.
def assign_crew(ship: Starship, crew_size: int) -> str:
    """Assigns crew and returns a confirmation message."""
    return f"{crew_size} crew assigned to the {ship.name}."
# [end]


def demo_core_annotations() -> None:
    ship = Starship("USS Enterprise")
    rename_ship(ship, "USS Enterprise-D")
    print(assign_crew(ship, 1014))
    print(ship.get_status_report())


# =============================================================================
# Type Specificity and Flexibility: Union, Any, and object
# =============================================================================

# [snippet: any-vs-object]
from typing import Any

# A union type for a value that might be missing.
# (Older code spells this Optional[int]; the two are the same type.)
command_code: int | None = 1701

def process_any(val: Any) -> None:
    # CHECKER SILENCED: this call is accepted for any argument, and raises
    # AttributeError at runtime if 'val' has no .upper() method.
    print(f"Processing any: {val.upper()}")

def process_object(val: object) -> None:
    # The checker rejects this: 'object' has no attribute 'upper'.
    #! print(f"Processing object: {val.upper()}")  # ERROR: "object" has no attribute "upper"

    # CHECKER PERMITTED: To use the value, you must first prove its type.
    if isinstance(val, str):
        # Inside this block, 'val' is narrowed to 'str'.
        print(f"Processing object as string: {val.upper()}")
# [end]


def demo_optional_spelling(code: "Optional[int]") -> None:
    """File-only check: Optional[X] is the older spelling of X | None."""
    from typing import assert_type

    assert_type(code, int | None)


from typing import Optional  # used only by the check above


def demo_any_vs_object() -> None:
    process_any("engage")
    process_object("engage")
    process_object(1701)  # prints nothing: not a str


# =============================================================================
# Handling Names Not Yet Defined (Forward References) -- Python 3.14 runtime
# =============================================================================

if sys.version_info >= (3, 14):
    # [snippet: forward-references]
    # Forward references work without quoting in Python 3.14.

    class Flagship:
        commander: Captain | None  # 'Captain' is not yet defined

        def __init__(self, name: str) -> None:
            self.name = name
            self.commander = None

        # The return type refers to the class while its body is still executing.
        def decommission(self) -> Flagship:
            print(f"{self.name} is now decommissioned.")
            return self

    class Captain:
        def __init__(self, name: str, ship: Flagship) -> None:
            self.name = name
            self.assigned_ship = ship
            ship.commander = self
    # [end]

    def demo_forward_references() -> None:
        # [snippet: forward-references]
        kirk = Captain("James T. Kirk", Flagship("USS Enterprise"))
        # [end]
        assert kirk.assigned_ship.decommission().commander is kirk


# =============================================================================
# Simplifying Complex Signatures with Type Aliases
# =============================================================================

# [snippet: alias-problem]
# This pattern might appear in several different function signatures.
def count_manifest_entries(manifest: dict[str, list[tuple[int, str]]]) -> int:
    return sum(len(records) for records in manifest.values())

def validate_crew_records(records: dict[str, list[tuple[int, str]]]) -> bool:
    return all(crew_id > 0 for crew in records.values() for crew_id, _ in crew)
# [end]


# [snippet: alias-solution]
# Use the 'type' statement to create aliases.
type CrewRecord = tuple[int, str]
type ShipManifest = dict[str, list[CrewRecord]]

# The function signature is now clean and self-documenting.
def process_ship_manifest(manifest: ShipManifest) -> None:
    for ship_class, records in manifest.items():
        print(f"Manifest for {ship_class}-class:")
        # The type checker knows 'records' is list[CrewRecord]
        # and 'record' is tuple[int, str]
        for record in records:
            crew_id, name = record
            print(f"  - ID: {crew_id}, Name: {name}")
# [end]


def demo_type_aliases() -> None:
    manifest: ShipManifest = {"Galaxy": [(1, "Picard"), (2, "Riker")]}
    process_ship_manifest(manifest)
    # An alias is interchangeable with the type it names.
    print(count_manifest_entries(manifest), validate_crew_records(manifest))


# =============================================================================
# Generic Type Aliases
# =============================================================================

# [snippet: generic-alias]
# Python 3.12+ (modern syntax)
type IDMap[K] = dict[K, list[K]]

def find_related_ids(mapping: IDMap[int], primary_id: int) -> list[int]:
    """Finds all IDs related to a primary integer ID."""
    return mapping.get(primary_id, [])

def find_related_names(mapping: IDMap[str], name: str) -> list[str]:
    """Finds all names related to a primary string name."""
    return mapping.get(name, [])
# [end]


def demo_generic_alias() -> None:
    # [snippet: generic-alias]
    # --- Usage ---
    int_relations: IDMap[int] = {101: [202, 303], 202: [101]}
    related_to_101 = find_related_ids(int_relations, 101)  # list[int]

    str_relations: IDMap[str] = {"riker": ["troi"], "troi": ["riker", "worf"]}
    related_to_troi = find_related_names(str_relations, "troi")  # list[str]
    # [end]
    print(related_to_101, related_to_troi)


# Legacy spelling of the same alias (pre-3.12). Mentioned in the guide's prose only.
from typing import TypeAlias, TypeVar

K = TypeVar("K")

LegacyIDMap: TypeAlias = dict[K, list[K]]


def demo_generic_alias_legacy() -> None:
    legacy_relations: LegacyIDMap[int] = {101: [202]}
    # Both spellings describe the same type.
    print(find_related_ids(legacy_relations, 101))


# =============================================================================
# Distinct Types with NewType
# =============================================================================

# [snippet: newtype]
from typing import NewType

USDCentsRaw = NewType("USDCentsRaw", int)
USDCentsValidated = NewType("USDCentsValidated", int)

def validate_cents(amount: USDCentsRaw) -> USDCentsValidated:
    """The one place where a raw amount becomes a validated one."""
    if amount < 0:
        raise ValueError("amount cannot be negative")
    return USDCentsValidated(amount)

def post_to_ledger(amount: USDCentsValidated) -> str:
    return f"Posted {amount} cents"
# [end]


# [snippet: newtype-vs-alias]
# By contrast, an alias is only another name for the same type.
type LooseCents = int

def post_loose(amount: LooseCents) -> str:
    return f"Posted {amount} cents"
# [end]


def demo_newtype() -> None:
    # [snippet: newtype]
    raw = USDCentsRaw(1999)
    print(post_to_ledger(validate_cents(raw)))

    # The checker rejects values that skipped validation:
    #! post_to_ledger(raw)  # ERROR: USDCentsRaw is not USDCentsValidated
    #! post_to_ledger(1999)  # ERROR: a bare int is not USDCentsValidated

    # No runtime wrapper: the value is still a plain int.
    assert type(raw) is int
    # [end]

    # [snippet: newtype-vs-alias]
    print(post_loose(1999))  # Accepted: LooseCents and int are the same type
    print(post_loose(raw))  # Accepted: nothing distinguishes the two
    # [end]


# =============================================================================
# Tuples: Structured Records vs. Uniform Collections
# =============================================================================

# [snippet: tuple-record]
# A record containing a starship's name, class, and active status.
# The shape is fixed: a string, then another string, then a boolean.
ship_record: tuple[str, str, bool] = ("USS Enterprise", "Galaxy", True)

def process_ship_record(record: tuple[str, str, bool]) -> None:
    name, ship_class, is_active = record  # statically checked unpacking
    status = "Active" if is_active else "Inactive"
    print(f"{name} ({ship_class}): {status}")
# [end]


def demo_tuple_record() -> None:
    # [snippet: tuple-record]
    process_ship_record(ship_record)

    # The type checker flags incorrect shapes or types:
    #! process_ship_record(("USS Voyager", "Intrepid"))  # ERROR: missing element
    #! process_ship_record((1701, "Galaxy", True))  # ERROR: first element is not a str
    # [end]


# [snippet: tuple-variadic]
# A collection of registry numbers of unknown length.
fleet_registry_numbers: tuple[int, ...] = (1701, 74656, 75294)

def get_smallest_ship_registry_number(registries: tuple[int, ...]) -> int:
    """Returns the smallest registry number in the collection."""
    return min(registries)
# [end]


def demo_tuple_variadic() -> None:
    # [snippet: tuple-variadic]
    # Valid call with a tuple of integers
    smallest = get_smallest_ship_registry_number((1701, 74656, 75294))

    # The type checker flags this call because the elements are not all integers.
    #! get_smallest_ship_registry_number((1701, "NX-01"))  # ERROR: element is not an int
    # [end]
    print(smallest)

    # tuple[int] is exactly one int; tuple[int, ...] is zero or more.
    exactly_one: tuple[int] = (1701,)
    #! too_many: tuple[int] = (1701, 74656)  # ERROR: tuple[int] holds exactly one element
    any_length: tuple[int, ...] = ()
    print(exactly_one, any_length)


# =============================================================================
# Type Inference and Resolution
# =============================================================================

def demo_common_type() -> None:
    # [snippet: common-type-ternary]
    from typing import assert_type

    is_text: bool = True  # could be True or False at runtime

    # The checker analyzes both branches of the conditional.
    # It sees a potential 'str' and a potential 'bytes'.
    data = "some text" if is_text else b"some_bytes"
    assert_type(data, str | bytes)
    # [end]

    # [snippet: common-type-list]
    # The checker inspects each element: int, str, float.
    mixed_data = [42, "answer", 6.022e23]
    # Checkers disagree here. pyright infers list[int | str | float];
    # mypy joins the element types and infers list[object].
    # Annotate the variable when the element type matters:
    measurements: list[int | str | float] = [42, "answer", 6.022e23]
    # [end]
    print(type(data).__name__, len(mixed_data), len(measurements))


def demo_numeric() -> None:
    # [snippet: numeric]
    from typing import assert_type

    int_val = 10
    float_val = 5.5

    # int + float is typed as float (and is a float at runtime).
    result = int_val + float_val
    assert_type(result, float)

    # The special case for float: an int is accepted where a float is expected.
    warp_factor: float = 9

    # bool is a subtype of int for the checker, exactly as at runtime.
    crew_delta: int = True
    # [end]
    print(result, warp_factor, crew_delta)


# [snippet: isinstance-narrowing]
def process_identifier(uid: str | int) -> None:
    # NOT PERMITTED: At this point the checker must account for both
    # possibilities (str and int), so a str-only method is rejected.
    #! print(uid.upper())  # ERROR: "int" has no attribute "upper"

    if isinstance(uid, str):
        # CHECK PASSES: On this branch, the checker treats uid as str,
        # so str-only operations are permitted.
        print(uid.upper())

    else:
        # CHECK FAILS: On this branch, the checker treats uid as int.
        # The same str-only operation remains not permitted here.
        #! print(uid.upper())  # ERROR: "int" has no attribute "upper"

        # int-specific operations are permitted instead.
        print(uid + 1000)
# [end]


# [snippet: truthiness]
def get_name_length(name: str | None) -> int:
    # Runtime meaning: this branch is taken only if name is not None and not "".
    # Type-checker effect: for str | None, this eliminates None.
    if name:
        return len(name)
    else:
        return 0
# [end]


# [snippet: assert-narrowing]
def must_be_string(uid: str | int) -> None:
    # The assertion proves to the checker that the non-str case is unreachable here.
    assert isinstance(uid, str), f"UID must be a string, but was {type(uid)}"

    # After the assertion, the checker narrows uid to str.
    print(uid.upper())
# [end]


def demo_conditional_resolution() -> None:
    process_identifier("ncc-1701")
    process_identifier(701)
    print(get_name_length("Picard"), get_name_length(""), get_name_length(None))
    must_be_string("riker")


# =============================================================================
# TypeIs
# =============================================================================

# [snippet: typeis]
from typing import TypeIs
from collections.abc import Sequence

def is_officer_manifest(manifest: Sequence[object]) -> TypeIs[Sequence[str]]:
    """
    Validates that a manifest sequence contains only officer names (strings).
    If this returns True, the type checker will treat manifest as Sequence[str] along that branch.
    """
    return all(isinstance(x, str) for x in manifest)

def log_officer_roster(roster: Sequence[object]) -> None:
    if is_officer_manifest(roster):
        # TYPE NARROWED: In this branch, the checker treats 'roster' as 'Sequence[str]'.
        print("Logging Officer Roster:")
        for name in roster:
            print(f"- Commander {name.title()}")
    else:
        # In this branch the checker makes no Sequence[str] assumption about 'roster'.
        print("Manifest contains invalid data; cannot log roster.")
# [end]


def demo_typeis() -> None:
    # [snippet: typeis]
    valid_roster = ["Picard", "Riker", "Data"]
    log_officer_roster(valid_roster)

    mixed_manifest = ("Lursa", "B'Etor", 2368)  # A tuple is a valid Sequence
    log_officer_roster(mixed_manifest)
    # [end]


# =============================================================================
# Structural Resolution: match
# =============================================================================

# [snippet: match]
from dataclasses import dataclass
from typing import assert_never

# 1. Define several distinct data structures.
@dataclass
class EngageCommand:
    warp_speed: float

@dataclass
class ReportStatusCommand:
    subsystem: str

@dataclass
class SetAlertCommand:
    level: str
    message: str | None = None

# 2. Create a union of these types.
type Command = EngageCommand | ReportStatusCommand | SetAlertCommand

def process_command(command: Command) -> str | float | None:
    match command:
        case EngageCommand(warp_speed=speed):
            # 'command' is EngageCommand here; 'speed' is float.
            print(f"Executing: Engage warp drive at speed {speed}.")
            return speed

        case ReportStatusCommand(subsystem=system):
            status = f"Report for {system}: All systems nominal."
            print(status)
            return status

        case SetAlertCommand(level=level, message=msg):
            suffix = f" ({msg})" if msg else ""
            print(f"Executing: Setting alert to {level.upper()}{suffix}.")
            return None

        case _:
            # Unreachable while every member of Command is handled above.
            # If a member is added to Command and not handled, the checker
            # reports an error on this line.
            assert_never(command)
# [end]


def demo_match() -> None:
    # [snippet: match]
    from typing import assert_type

    # --- Static type check at the call site ---
    some_command: Command = EngageCommand(warp_speed=9.1)
    result = process_command(some_command)

    # The call site sees the function's declared return type,
    # whichever branch actually ran.
    assert_type(result, str | float | None)
    # [end]
    process_command(ReportStatusCommand("warp core"))
    process_command(SetAlertCommand("red", "Borg cube detected"))


def demo_resolution_forms(unknown: Any, known: str | int) -> None:
    """File-only check: one isinstance test materializes Any and narrows a union."""
    from typing import assert_type

    assert_type(unknown, Any)
    if isinstance(unknown, str):
        assert_type(unknown, str)  # materialized: Any -> str
    assert_type(known, str | int)
    if isinstance(known, str):
        assert_type(known, str)  # narrowed: str | int -> str


def demo_exhaustiveness(command: Command) -> None:
    """File-only check: assert_never rejects a value that can still be something."""
    if isinstance(command, EngageCommand):
        return
    #! assert_never(command)  # ERROR: two members of Command are still possible


# =============================================================================
# Advanced Narrowing: Promises vs. Proof
# =============================================================================

# [snippet: guard-vs-cast]
from typing import Literal, TypedDict, TypeIs, cast, get_args

type ShipIdKey = Literal["name", "registry"]

class ShipIdCard(TypedDict):
    name: str
    registry: str

# The type guard (proof)
def is_ship_id_key(key: str) -> TypeIs[ShipIdKey]:
    # A 'type' statement creates a TypeAliasType object; the aliased type is its
    # __value__. get_args(ShipIdKey) on the alias itself returns ().
    return key in get_args(ShipIdKey.__value__)

def update_with_guard(record: ShipIdCard, key: str, value: str) -> None:
    # A real runtime check occurs here.
    if is_ship_id_key(key):
        # This assignment is permitted because the invalid cases
        # were eliminated by the guard.
        record[key] = value
    else:
        print(f"'{key}' is not a valid key.")

def update_with_cast(record: ShipIdCard, key: str, value: str) -> None:
    # This is an unconditional promise. No runtime check occurs.
    valid_key = cast(ShipIdKey, key)

    # The assignment is permitted because the checker was told to treat
    # 'valid_key' as a ShipIdKey.
    record[valid_key] = value
# [end]


def demo_guard_vs_cast() -> None:
    # [snippet: guard-vs-cast]
    # --- Usage ---
    ship = ShipIdCard(name="Voyager", registry="NCC-74656")

    # Correct usage works for both
    update_with_guard(ship, "name", "Enterprise")
    update_with_cast(ship, "registry", "NCC-1701-D")

    # Incorrect usage
    update_with_guard(ship, "captain", "Janeway")  # Rejected by the runtime check.
    update_with_cast(ship, "captain", "Janeway")  # Passes static checking AND raises nothing:
    # a TypedDict is a plain dict at runtime, so the broken promise silently
    # adds a 'captain' key that ShipIdCard does not allow.
    # [end]
    print(sorted(ship))


# =============================================================================
# Typing Data from the Edge: TypedDict
# =============================================================================

# [snippet: typeddict-edge]
import json
from typing import TypedDict

class StarshipData(TypedDict):
    name: str
    registry: str
    crew_count: int
    is_commissioned: bool

raw_json_payload = """
{
    "name": "USS Enterprise",
    "registry": "NCC-1701-D",
    "crew_count": 1014,
    "is_commissioned": true
}
"""

def register_ship(ship_record: StarshipData) -> None:
    print(f"Registering {ship_record['registry']}: {ship_record['name']}")
    if ship_record['is_commissioned']:
        print(f"Crew complement: {ship_record['crew_count']}")
# [end]


def demo_typeddict_edge() -> None:
    # [snippet: typeddict-edge]
    # At the boundary, load the data and annotate it as the expected shape.
    ship_data: StarshipData = json.loads(raw_json_payload)

    register_ship(ship_data)
    # [end]


# [snippet: typeddict-notrequired]
from typing import NotRequired, TypedDict

class ShipHistoryData(TypedDict):
    # These keys must be present.
    name: str
    registry: str

    # This key may be missing entirely.
    commission_date: NotRequired[int]
# [end]


# [snippet: typeddict-in]
def describe_ship_history(data: ShipHistoryData) -> None:
    # Required keys can be accessed directly.
    print(f"Processing {data['name']} ({data['registry']})")

    # Check for an optional key before using it.
    if "commission_date" in data:
        # Inside this branch, the checker treats the key as present.
        print(f"Commissioned in {data['commission_date']}")
# [end]


# [snippet: typeddict-get]
def describe_ship_history_with_get(data: ShipHistoryData) -> None:
    commission_date = data.get("commission_date")
    if commission_date is not None:
        # Here, the checker knows the value exists and is an int.
        print(f"Commissioned in {commission_date}")
# [end]


def demo_typeddict_optional_keys() -> None:
    describe_ship_history({"name": "USS Enterprise", "registry": "NCC-1701-D", "commission_date": 2363})
    describe_ship_history({"name": "USS Pegasus", "registry": "NCC-53847"})
    describe_ship_history_with_get({"name": "USS Voyager", "registry": "NCC-74656", "commission_date": 2371})
    describe_ship_history_with_get({"name": "USS Pegasus", "registry": "NCC-53847"})


# =============================================================================
# The Robust Solution: Parsing into Data Classes
# =============================================================================

# [snippet: dataclass-boundary]
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self

@dataclass
class StarshipRecord:
    name: str
    registry: str
    crew_count: int
    is_commissioned: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Self:
        """
        Parse and validate raw input data, raising if constraints are violated.
        This is the boundary where untyped input is converted into a typed value.
        """
        # The values are 'object', so the checker demands proof before each use.
        # A missing key raises KeyError.
        name = data["name"]
        registry = data["registry"]
        crew_count = data["crew_count"]
        is_commissioned = data["is_commissioned"]

        if not isinstance(name, str):
            raise TypeError("name must be a str")
        if not isinstance(registry, str):
            raise TypeError("registry must be a str")
        # bool is a subclass of int, so it has to be excluded explicitly.
        if isinstance(crew_count, bool) or not isinstance(crew_count, int):
            raise TypeError("crew_count must be an int")
        if crew_count < 0:
            raise ValueError("crew_count cannot be negative")
        if not isinstance(is_commissioned, bool):
            raise TypeError("is_commissioned must be a bool")

        return cls(
            name=name,
            registry=registry,
            crew_count=crew_count,
            is_commissioned=is_commissioned,
        )

    def get_status_report(self) -> str:
        status = "Active" if self.is_commissioned else "Decommissioned"
        return f"{self.name} ({self.registry}) - Status: {status}"
# [end]


def demo_dataclass_boundary() -> None:
    # [snippet: dataclass-usage]
    raw_data = json.loads(raw_json_payload)
    enterprise = StarshipRecord.from_dict(raw_data)

    print(enterprise.get_status_report())
    # [end]


# =============================================================================
# Typing Synchronous Functions and Methods
# =============================================================================

# [snippet: callable]
from collections.abc import Callable

# 'op' accepts two integers and returns an integer
def apply_operation(a: int, b: int, op: Callable[[int, int], int]) -> int:
    return op(a, b)

# Common patterns:
# No parameters: Callable[[], str]
# No return: Callable[[str], None]
# Unchecked signature: Callable[..., Any]
# [end]


# [snippet: never]
from typing import Never

def fail_with_error(message: str) -> Never:
    raise ValueError(message)

def stringify(value: str | int) -> str:
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, int):
        return str(value)
    else:
        # The checker knows this branch is unreachable because 'value'
        # has been exhausted. Calling a Never function documents this.
        fail_with_error(f"Unexpected type: {type(value)}")
# [end]


# [snippet: self-type]
from typing import Self

class Cruiser(Starship):
    def set_warp_speed(self, speed: int) -> Self:
        self.warp_speed = speed
        return self

class Battlecruiser(Cruiser):
    def arm_weapons(self) -> Self:
        self.weapons_armed = True
        return self
# [end]


def demo_self_type() -> None:
    # [snippet: self-type]
    from typing import assert_type

    # set_warp_speed() is defined on Cruiser, yet the chain stays a Battlecruiser.
    ship = Battlecruiser("IKS Rotarran").set_warp_speed(9).arm_weapons()
    assert_type(ship, Battlecruiser)
    # [end]
    print(type(ship).__name__, ship.warp_speed, ship.weapons_armed)


# [snippet: override]
from typing import override

# Starship.get_status_report() -> str is defined under "Core Annotation Syntax".
class Warbird(Starship):
    @override
    def get_status_report(self) -> str:
        return f"{self.name}: Cloaked."

    #! @override
    #! def get_statis_report(self) -> str:  # ERROR: no parent method has this name
    #!     return "Status: Unknown"
# [end]


def demo_sync_functions() -> None:
    print(apply_operation(6, 7, lambda a, b: a * b))
    print(stringify("warp"), stringify(9))
    print(Warbird("IRW Khazara").get_status_report())


# =============================================================================
# Typing Asynchronous Code
# =============================================================================

# [snippet: async-def]
import asyncio

async def fetch_ship_status(registry_id: str) -> str:
    await asyncio.sleep(0.01)
    return f"Status for {registry_id}: All systems nominal."
# [end]


# [snippet: async-usage]
from typing import Any
from collections.abc import Awaitable, Callable, Coroutine

async def log_status_from_source(source: Awaitable[str]) -> None:
    status_report = await source
    print(f"LOG: {status_report.upper()}")

async def status_briefing() -> None:
    # Reference: as a value, the async function is a Callable returning an awaitable.
    fetcher: Callable[[str], Awaitable[str]] = fetch_ship_status

    # Calling it runs none of its body; it only creates a coroutine object.
    status_coro: Coroutine[Any, Any, str] = fetch_ship_status("NCC-1701-D")

    # Use: awaiting consumes the computation and yields a str.
    await log_status_from_source(status_coro)
    await log_status_from_source(fetcher("NCC-74656"))
# [end]


def demo_async() -> None:
    asyncio.run(status_briefing())


# [snippet: coroutine-vs-generator]
from typing import Any
from collections.abc import Coroutine, Generator

# A generator function's annotation names the object that the call returns:
# Generator[...], or a supertype of it such as Iterator[int].
def count_decks(top: int) -> Generator[int, None, str]:
    for deck in range(1, top + 1):
        yield deck
    return "all decks reported"

# An async function's annotation names only the final, awaited value.
async def report_decks() -> str:
    return "all decks reported"

# Annotating a generator function the coroutine way is rejected:
#! def miscounted() -> int: yield 1  # ERROR: must be Generator or one of its supertypes
# [end]


def count_decks_as_iterator(top: int) -> "Iterator[int]":
    """File-only check: Iterator is an accepted annotation for a generator function."""
    yield from range(1, top + 1)


from collections.abc import Iterator  # used only by the check above


def demo_coroutine_vs_generator() -> None:
    # [snippet: coroutine-vs-generator]
    from typing import assert_type

    decks = count_decks(3)
    assert_type(decks, Generator[int, None, str])  # exactly what was written

    pending: Coroutine[Any, Any, str] = report_decks()  # a Coroutine around what was written
    # [end]
    print(list(decks), asyncio.run(pending))


# =============================================================================
# Creating Generic Functions with TypeVar
# =============================================================================

# [snippet: generic-function]
from collections.abc import Sequence

# [T] declares a type variable (Python 3.12+): a consistent, but undetermined, type.
def get_first_element[T](items: Sequence[T]) -> T:
    """
    Returns the first element of a sequence while
    maintaining the specific type correlation.
    """
    if not items:
        raise ValueError("Sequence cannot be empty")
    return items[0]
# [end]


def demo_generic_function() -> None:
    # [snippet: generic-function]
    # --- Static Analysis Resolution ---

    # The checker binds T to 'str'. The return is analyzed as 'str'.
    name: str = get_first_element(["Worf", "Data"])

    # The checker binds T to 'int'. The return is analyzed as 'int'.
    code: int = get_first_element([1701, 74656])

    #! wrong: int = get_first_element(["Worf", "Data"])  # ERROR: T is str here, not int
    # [end]
    print(name, code)


# [snippet: generic-function-legacy]
from typing import TypeVar

T = TypeVar("T")

def get_first_element_legacy(items: Sequence[T]) -> T:
    return items[0]
# [end]


# [snippet: typevar-bound]
from collections.abc import Sequence

# ShipT must be Starship or a subclass (legacy: TypeVar("ShipT", bound=Starship)).
def first_to_report[ShipT: Starship](fleet: Sequence[ShipT]) -> ShipT:
    """
    The bound lets the checker verify that .get_status_report() is valid for
    every element, while the return type stays as specific as the argument.
    """
    for ship in fleet:
        print(f"- {ship.get_status_report()}")
    return fleet[0]
# [end]


def demo_typevar_bound() -> None:
    # [snippet: typevar-bound]
    from typing import assert_type

    lead = first_to_report([Warbird("IRW Khazara"), Warbird("IRW Belak")])
    assert_type(lead, Warbird)  # not widened to Starship

    #! first_to_report(["not", "ships"])  # ERROR: str does not satisfy the bound
    # [end]
    print(get_first_element_legacy([lead.name]))


# [snippet: typevar-constraints]
# T must be solved to exactly str or exactly bytes
# (legacy spelling: T = TypeVar("T", str, bytes)).
def concatenate[T: (str, bytes)](left: T, right: T) -> T:
    return left + right
# [end]


class Callsign(str):
    """A str subclass, used to show how a constrained type variable is solved."""


def demo_typevar_constraints() -> None:
    # [snippet: typevar-constraints]
    from typing import assert_type

    assert_type(concatenate("NCC", "-1701"), str)
    assert_type(concatenate(b"NCC", b"-1701"), bytes)

    # A subclass of str is accepted, and T is solved to str itself:
    assert_type(concatenate(Callsign("NCC"), Callsign("-1701")), str)

    #! concatenate("NCC", b"-1701")  # ERROR: str and bytes cannot be mixed
    #! concatenate(1701, 74656)  # ERROR: int is not one of the listed types
    # [end]
    print(concatenate("NCC", "-1701"), concatenate(b"NCC", b"-1701"))


# =============================================================================
# Variance
# =============================================================================

def demo_invariance() -> None:
    # [snippet: invariance]
    from collections.abc import Sequence

    warbirds: list[Warbird] = [Warbird("IRW Khazara")]

    #! starships: list[Starship] = warbirds  # ERROR: list is invariant
    read_only: Sequence[Starship] = warbirds  # Accepted: Sequence is covariant
    # [end]
    print(len(read_only))


# [snippet: covariance]
from typing import Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)

class Logbook(Generic[T_co]):
    """A read-only logbook; T_co is only used in an output position."""

    def __init__(self, *entries: T_co) -> None:
        self._entries = entries

    def get_latest_entry(self) -> T_co:
        return self._entries[-1]

def analyze_starship_log(log: Logbook[Starship]) -> None:
    print(f"Latest entry: {log.get_latest_entry().get_status_report()}")
# [end]


# [snippet: contravariance]
from typing import Generic, TypeVar

T_contra = TypeVar("T_contra", contravariant=True)

class RepairScheduler(Generic[T_contra]):
    """Schedules a ship for repair; T_contra is only used in an input position."""

    def __init__(self) -> None:
        self.scheduled = 0

    def schedule_repair(self, ship: T_contra) -> None:
        self.scheduled += 1
        print(f"Repair #{self.scheduled} scheduled.")

def service_warbird_fleet(scheduler: RepairScheduler[Warbird], fleet: Sequence[Warbird]) -> None:
    for ship in fleet:
        scheduler.schedule_repair(ship)
# [end]


# [snippet: variance-inferred]
# Python 3.12+ class syntax: no variance keyword. The checker infers that T is
# covariant because it only appears in output positions.
class Archive[T]:
    def __init__(self, *entries: T) -> None:
        self._entries = entries

    def latest(self) -> T:
        return self._entries[-1]

def review_archive(archive: Archive[Starship]) -> None:
    print(f"Archived: {archive.latest().get_status_report()}")
# [end]


def demo_variance() -> None:
    # [snippet: covariance]
    warbird_log = Logbook(Warbird("IRW Khazara"))  # Logbook[Warbird]
    # Valid: The more specific log can be used where a general one is expected.
    analyze_starship_log(warbird_log)
    # [end]

    # [snippet: contravariance]
    general_scheduler = RepairScheduler[Starship]()
    # Valid: The more general scheduler can fulfill the role of a specific one.
    service_warbird_fleet(general_scheduler, [Warbird("IRW Khazara")])
    # [end]

    # The reverse directions are rejected.
    starship_log = Logbook(Starship("USS Enterprise"))
    print(starship_log.get_latest_entry().name)

    def analyze_warbird_log(log: Logbook[Warbird]) -> None:
        print(log.get_latest_entry().name)

    #! analyze_warbird_log(starship_log)  # ERROR: Logbook[Starship] is not a Logbook[Warbird]
    analyze_warbird_log(warbird_log)

    # [snippet: variance-inferred]
    review_archive(Archive(Warbird("IRW Khazara")))  # Archive[Warbird] accepted
    # [end]


# =============================================================================
# Advanced Generic Callables: Higher-Order Functions
# =============================================================================

# [snippet: hof-typevar]
from collections.abc import Callable

# Two type variables represent the input and output types.
def transform_value[InputType, OutputType](
    transformer: Callable[[InputType], OutputType],
    value: InputType,
) -> OutputType:
    """Applies a transformer function to a value."""
    return transformer(value)
# [end]


def demo_hof_typevar() -> None:
    # [snippet: hof-typevar]
    # --- Usage Examples ---

    # 1. Transforming an integer to a string
    crew_size: int = 1014
    # InputType is solved as 'int', OutputType is solved as 'str'.
    report: str = transform_value(str, crew_size)

    # 2. Transforming a string to an integer
    registry: str = "NCC-1701-D"
    # InputType is 'str', OutputType is 'int'.
    def get_ship_number(reg: str) -> int:
        return int(reg.split('-')[1])

    ship_number: int = transform_value(get_ship_number, registry)

    #! transform_value(get_ship_number, crew_size)  # ERROR: int passed where str is required
    # [end]
    print(report, ship_number)


# [snippet: typevartuple]
# [*Ts] declares a TypeVarTuple (Python 3.12+): it stands for a sequence of
# types such as (str, int, bool). Legacy spelling: Ts = TypeVarTuple("Ts").
def apply_operations[*Ts](*args: *Ts) -> tuple[*Ts]:
    """
    Accepts heterogeneous positional arguments and preserves their
    individual types across the function boundary.
    """
    return args
# [end]


def demo_typevartuple() -> None:
    # [snippet: typevartuple]
    from typing import assert_type

    # The type checker solves for 'Ts' by inspecting the arguments.
    # It infers that Ts = (str, int, bool)
    result = apply_operations("USS Enterprise", 1701, True)
    assert_type(result, tuple[str, int, bool])

    ship_name = result[0]  # str
    registry_num = result[1]  # int

    # The analyzer can now flag incorrect usage:
    #! result[1].upper()  # ERROR: "int" has no attribute "upper"
    #! result[0] + 5  # ERROR: unsupported operand types for + ("str" and "int")
    # [end]
    print(ship_name, registry_num)

    # A pack cannot be used as a single type argument; it has to be expanded.
    #! def packed[*Xs](*args: *Xs) -> tuple[Xs]: return args  # ERROR: Xs must be unpacked


# [snippet: typevartuple-class]
# A generic class that holds a specific sequence of types.
# *Ts expands the type pack into individual type arguments.
class Record[*Ts]:
    def __init__(self, *items: *Ts) -> None:
        self._items = items

    def get_items(self) -> tuple[*Ts]:
        return self._items
# [end]


def demo_typevartuple_class() -> None:
    # [snippet: typevartuple-class]
    from typing import assert_type

    # --- Usage Example ---

    # This Record holds a string, an integer, and a boolean.
    # The type checker solves Ts = (str, int, bool).
    ship_log: Record[str, int, bool] = Record("Enterprise", 1701, True)

    # The type checker knows the exact return type of get_items().
    items = ship_log.get_items()
    assert_type(items, tuple[str, int, bool])

    # This allows positional access with complete type information for each element.
    registry_num = items[1]  # int

    # The analyzer can flag operations inconsistent with the inferred types:
    #! items[0] + 10  # ERROR: unsupported operand types for + ("str" and "int")
    #! items[2].upper()  # ERROR: "bool" has no attribute "upper"

    # Note: Ts is a static-analysis abstraction. At runtime, Record instances
    # behave like ordinary Python objects with no special type-pack handling.
    # [end]
    print(registry_num)


# [snippet: unpack-legacy]
from typing import Generic, TypeVarTuple, Unpack

LegacyTs = TypeVarTuple("LegacyTs")

# Identical in meaning to 'class Record[*Ts]' above.
class LegacyRecord(Generic[Unpack[LegacyTs]]):
    def __init__(self, *items: Unpack[LegacyTs]) -> None:
        self._items = items

    def get_items(self) -> tuple[Unpack[LegacyTs]]:
        return self._items
# [end]


# [snippet: unpack-kwargs]
from typing import Literal, NotRequired, TypedDict, Unpack

class AlertOptions(TypedDict):
    level: Literal["yellow", "red"]
    message: NotRequired[str]

def raise_alert(**kwargs: Unpack[AlertOptions]) -> str:
    message = kwargs.get("message", "no details")
    return f"{kwargs['level'].upper()} ALERT: {message}"
# [end]


def demo_unpack() -> None:
    from typing import assert_type

    legacy = LegacyRecord("Defiant", 74205)
    assert_type(legacy.get_items(), tuple[str, int])
    print(legacy.get_items())

    # [snippet: unpack-kwargs]
    print(raise_alert(level="red", message="Shields down"))
    print(raise_alert(level="yellow"))

    #! raise_alert(level="purple")  # ERROR: not one of the permitted literals
    #! raise_alert(severity="red")  # ERROR: unknown keyword, and 'level' is missing
    # [end]


# =============================================================================
# Advanced Generic Callables: Wrappers
# =============================================================================

# [snippet: naive-decorator]
from typing import Any
from collections.abc import Callable

def naive_logging_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator that loses all type information."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling function: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@naive_logging_decorator
def set_course(ship_class: str, heading: int) -> None:
    # These operations assume correct argument order and types.
    print(f"Setting course for {ship_class.upper()} at heading {heading + 1}")
# [end]


def demo_naive_decorator() -> None:
    # [snippet: naive-decorator]
    # The type checker has lost the original signature.
    # It now sees 'set_course' as '(*args: Any, **kwargs: Any) -> Any',
    # so this reversed call is NOT flagged.
    try:
        set_course(90, "Enterprise")
    except AttributeError as exc:
        # The first bad operation fails at runtime: (90).upper()
        print(f"Runtime failure: {exc}")
    # [end]
    set_course("Galaxy", 89)


# [snippet: paramspec]
import functools
from collections.abc import Callable

# [**P, R] declares a ParamSpec and a TypeVar (Python 3.12+).
# Legacy spelling: P = ParamSpec("P"); R = TypeVar("R").
def fully_typed_logging_decorator[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """A decorator that preserves the wrapped function's signature."""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Log: Calling {func.__name__} with arguments {args} and {kwargs}")
        result = func(*args, **kwargs)
        print(f"Log: {func.__name__} returned {result!r}")
        return result
    return wrapper

@fully_typed_logging_decorator
def staff_ship_class(ship_class: str, crew_size: int) -> str:
    """Assigns crew and returns a confirmation message."""
    return f"{crew_size} crew assigned to {ship_class}-class starship."

@fully_typed_logging_decorator
def set_alert_status(status: str = "green") -> None:
    """Sets the ship's alert status."""
    print(f"Alert status is now {status}.")
# [end]


def demo_paramspec() -> None:
    # [snippet: paramspec]
    # --- Usage Example ---

    # The type checker knows the exact signature of the decorated function:
    # staff_ship_class(ship_class: str, crew_size: int) -> str
    confirmation: str = staff_ship_class("Galaxy", 1014)

    # It also understands default arguments and return types:
    # set_alert_status(status: str = "green") -> None
    set_alert_status(status="red")
    set_alert_status()

    # Most importantly, it now catches type errors immediately:
    #! staff_ship_class("Sovereign", "a lot")  # ERROR: expected int, not str
    #! set_alert_status(1)  # ERROR: expected str, not int
    # [end]
    print(confirmation)


# =============================================================================
# Literal, Final, @final, ClassVar
# =============================================================================

# [snippet: literal]
from typing import Literal

# The 'mode' parameter can only be one of three specific string values.
def set_warp_drive_mode(mode: Literal["standby", "engage", "emergency"]) -> None:
    print(f"Warp drive mode set to: {mode}")
# [end]


def demo_literal() -> None:
    # [snippet: literal]
    set_warp_drive_mode("engage")  # Accepted
    #! set_warp_drive_mode("full_speed")  # ERROR: not one of the permitted values
    # [end]


# [snippet: final-constant]
from typing import Final

# MAX_WARP is a constant and should not be changed.
MAX_WARP: Final[float] = 9.975

#! MAX_WARP = 10.0  # ERROR: cannot assign to a Final name

# Final forbids rebinding the name. It does not make the object immutable.
DECK_NUMBERS: Final[list[int]] = [1, 2]
DECK_NUMBERS.append(3)  # Accepted
# [end]


# [snippet: final-class]
from typing import final

@final
class EmergencyBroadcastSystem:
    """This system's implementation is fixed and should not be altered."""
    def send_universal_alert(self, message: str) -> None:
        print(f"ALERT: {message.upper()}")

# The type checker flags this subclass:
#! class ModifiedBroadcastSystem(EmergencyBroadcastSystem):  # ERROR: cannot inherit from a final class
#!     def send_universal_alert(self, message: str) -> None:
#!         print("This is a modified, unauthorized alert!")
# [end]


# [snippet: final-method]
from typing import final, override

class Probe:
    def __init__(self, serial: str) -> None:
        self._serial = serial

    @final
    def get_serial_id(self) -> str:
        """
        The serial ID is fundamental to a probe's identity
        and its retrieval logic must not be changed.
        """
        return f"ID-{self._serial}"

    def get_status_report(self) -> str:
        """Subclasses are free to override this method."""
        return "Status: All systems nominal."


class StealthProbe(Probe):
    # This is valid: get_status_report() is not final.
    @override
    def get_status_report(self) -> str:
        return "Status: Cloaked."

    # The type checker flags this override:
    #! def get_serial_id(self) -> str:  # ERROR: cannot override a final method
    #!     return f"CLOAKED-{self._serial}"
# [end]


# [snippet: classvar]
from typing import ClassVar

class Runabout:
    # This attribute is shared across all Runabout instances.
    registry_prefix: ClassVar[str] = "NCC"

    def __init__(self, designation: int) -> None:
        # This is an instance attribute, unique to each object.
        self.designation: int = designation
# [end]


def demo_constraints() -> None:
    print(MAX_WARP)
    EmergencyBroadcastSystem().send_universal_alert("red alert")
    probe = StealthProbe("7")
    print(probe.get_serial_id(), probe.get_status_report())

    # [snippet: classvar]
    danube = Runabout(72003)
    rio_grande = Runabout(72452)

    print(danube.registry_prefix)  # Prints "NCC"
    print(rio_grande.registry_prefix)  # Also prints "NCC"

    # A ClassVar cannot be assigned through an instance:
    #! danube.registry_prefix = "USS"  # ERROR: cannot assign to a class variable via an instance

    Runabout.registry_prefix = "USS"  # Modifying the class var affects all instances
    print(danube.registry_prefix)  # Now prints "USS"
    # [end]
    Runabout.registry_prefix = "NCC"


# =============================================================================
# Appendix 1: Protocol
# =============================================================================

# [snippet: protocol]
from typing import Protocol

# 1. Define the "interface" or structural contract.
# Any object that has a .name attribute of type str and a .get_status()
# method returning str will be considered "Reportable".
class Reportable(Protocol):
    name: str
    def get_status(self) -> str:
        ...  # The ellipsis indicates no implementation is needed in the protocol

# 2. Write a function that depends on the protocol, not a concrete class.
def print_status_report(item: Reportable) -> None:
    """This function works with ANY object that matches the Reportable shape."""
    print(f"Report for {item.name}: {item.get_status()}")

# 3. Define concrete classes that implicitly satisfy the protocol.
#    Note that they do NOT inherit from Reportable.
class Freighter:
    def __init__(self, name: str, is_active: bool) -> None:
        self.name = name
        self.is_active = is_active

    def get_status(self) -> str:
        return "Active" if self.is_active else "Decommissioned"

class Subsystem:
    def __init__(self, name: str, power_level: float) -> None:
        self.name = name
        self.power_level = power_level

    def get_status(self) -> str:
        return f"Online at {self.power_level}%"

# The right names are not enough: the member types must be compatible too.
class Mislabeled:
    name: int = 1701

    def get_status(self) -> int:
        return 0
# [end]


def demo_protocol() -> None:
    # [snippet: protocol]
    # 4. Use the function with different, unrelated types.
    freighter = Freighter("SS Xhosa", is_active=True)
    warp_core = Subsystem("Warp Core", 99.8)

    # Both calls are accepted because both Freighter and Subsystem
    # structurally match the Reportable protocol.
    print_status_report(freighter)
    print_status_report(warp_core)

    # An object without the required shape is rejected:
    #! print_status_report("just a string")  # ERROR: str is not Reportable
    #! print_status_report(Mislabeled())  # ERROR: right names, incompatible types
    # [end]


# =============================================================================
# Appendix 1: Runtime validation with Pydantic
# =============================================================================

# [snippet: pydantic]
import json
from pydantic import BaseModel, ValidationError

# 1. Define your data structure using Pydantic's BaseModel.
#    The syntax is nearly identical to a dataclass.
class StarshipModel(BaseModel):
    name: str
    registry: str
    crew_count: int
    is_commissioned: bool

# 2. An incoming JSON payload that contains an error.
#    'crew_count' is a string, not an integer as required.
invalid_json_payload = """
{
    "name": "USS Enterprise",
    "registry": "NCC-1701-D",
    "crew_count": "one thousand and fourteen",
    "is_commissioned": true
}
"""
# [end]


def demo_pydantic() -> None:
    # [snippet: pydantic]
    raw_data = json.loads(invalid_json_payload)

    # 3. At the boundary, attempt to parse the raw data into your Pydantic model.
    try:
        # Pydantic validates and, in its default mode, converts compatible
        # input (the string "1014" would become the int 1014). Here it fails:
        # "one thousand and fourteen" cannot be converted to an integer.
        enterprise = StarshipModel.model_validate(raw_data)
        print(f"Successfully registered {enterprise.name}!")
    except ValidationError as e:
        # If validation fails, Pydantic raises a detailed error.
        print("Failed to parse starship data. Errors:")
        print(e)

    # Output:
    # Failed to parse starship data. Errors:
    # 1 validation error for StarshipModel
    # crew_count
    #   Input should be a valid integer, unable to parse string as an integer [type=int_parsing, ...
    # [end]


# =============================================================================
# Run everything, in guide order
# =============================================================================

def main() -> None:
    demos: list[Callable[[], None]] = [
        demo_builtin_generics,
        demo_core_annotations,
        demo_any_vs_object,
        demo_type_aliases,
        demo_generic_alias,
        demo_generic_alias_legacy,
        demo_newtype,
        demo_tuple_record,
        demo_tuple_variadic,
        demo_common_type,
        demo_numeric,
        demo_conditional_resolution,
        demo_typeis,
        demo_match,
        demo_guard_vs_cast,
        demo_typeddict_edge,
        demo_typeddict_optional_keys,
        demo_dataclass_boundary,
        demo_sync_functions,
        demo_self_type,
        demo_async,
        demo_coroutine_vs_generator,
        demo_generic_function,
        demo_typevar_bound,
        demo_typevar_constraints,
        demo_invariance,
        demo_variance,
        demo_hof_typevar,
        demo_typevartuple,
        demo_typevartuple_class,
        demo_unpack,
        demo_naive_decorator,
        demo_paramspec,
        demo_literal,
        demo_constraints,
        demo_protocol,
        demo_pydantic,
    ]
    if sys.version_info >= (3, 14):
        demos.insert(3, demo_forward_references)
    for demo in demos:
        print(f"\n=== {demo.__name__} ===")
        demo()


if __name__ == "__main__":
    main()

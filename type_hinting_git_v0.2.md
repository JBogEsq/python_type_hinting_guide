# Copyright © 2026. All rights reserved.

# Overview of Python Type Hinting (aka typing)

## Preface

This is a type hinting guide for Python 3.14. There may be references to older Python versions throughout, but users of Python 3.13 or earlier should expect differences in behavior and syntax and should not rely on this guide as authoritative for those versions.

This guide supplements Python’s official documentation; it does not replace it. For a formal specification, consult the [standard library](https://docs.python.org/3/library/typing.html) or [typing module](https://typing.python.org/en/latest/spec/index.html). For quick reference, see the standard [cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) and the [typing best practices](https://typing.python.org/en/latest/reference/best_practices.html) guide.

This guide avoids mere repackaging of those resources. Instead, it presents the typing ecosystem as a conceptual tool for expressing architectural intent and semantic constraints that are difficult or impossible to express with Python’s unenriched syntax.

**How the examples were validated.** Every Python block in this guide is an excerpt of `typing_guide_examples.py`, a single runnable module, and is exercised by `test_typing_guide_examples.py`. The module passes `mypy --strict` (mypy 2.3.1, targeting Python 3.14), and its runtime behavior is tested on CPython 3.13. A commented line marked `# ERROR` is code that a checker must reject; each one was uncommented in a copy of the module and confirmed to be reported by mypy, with no errors anywhere else. Two limits apply: the examples were not run against pyright, so statements about pyright are from its documented behavior, and the unquoted forward-reference example needs the Python 3.14 runtime, so it was type-checked but not executed.

## [Brief Discussion of Type Theory, Type Systems, and Role of Type Hinting](https://typing.python.org/en/latest/spec/concepts.html#)

Type theory is a family of formal frameworks for reasoning about the structural relationships between entities—objects, functions, or processes—by classifying them according to the properties and operations they admit. In these systems, a type is a constraint: it specifies properties that values must satisfy. Programming languages adopt and adapt fragments of this tradition in different ways. Python’s typing system is one such adaptation: it borrows the vocabulary and some of the abstractions of type theory while deliberately separating them from runtime enforcement, using them instead to support static analysis and developer understanding. In Python, this results in a practical use of types as tools for reasoning about code, rather than as constraints on execution.

As a general proposition, a programming language's approach to types is known as its type system.  In practice, the terminology used to describe type systems in programming languages is informal and enforcement-oriented, so descriptions typically focus on where and when types are enforced (code, compilation, or runtime).  Those languages that assign every "object" to a type and ensure that only permitted type operations are called on those objects are known as a type-safe languages.  Programming languages that enforce type safety prior to execution (runtime) are known as statically typed languages.  Programming languages that enforce type safety at runtime are known as dynamically typed languages.  Theoretically speaking, any language that is untyped is inherently a non-type safe language.  Type-safe languages are said to provide "structural safety."

Python recognizes the value of static type analysis for detecting mismatches between intended and actual object usage prior to execution, while remaining a dynamically typed language by design. The interpreter does not enforce type annotations, and they do not affect runtime semantics. To obtain the benefits of static analysis without sacrificing dynamic execution, Python provides an optional type hinting ecosystem consisting of syntax and supporting tools (IDEs, mypy, pyright).

Note: In this document, “type hints” and “type annotations” are used interchangeably unless technical usage requires otherwise. Technically, a type hint is the role a type annotation plays, while a [type annotation](https://typing.python.org/en/latest/spec/annotations.html) is the syntax used to provide a type hint.

Remember, because the interpreter ignores type hints, annotated functions will still accept incompatible values at runtime (e.g., a function annotated to accept int will accept str), potentially raising a TypeError. Accordingly, Python’s type hints support analysis rather than enforcement and do not convert Python into a type-safe system. The distinction between Python’s dynamic typing model and a formally type-safe system is beyond the scope of this overview.

### Duck Typing Remains Python's Idiomatic Approach

Duck typing — if it walks like a duck and quacks like a duck, it is a duck — remains Python's preferred approach at runtime for determining whether a particular operation, its arguments, and its returns are appropriate (i.e., runtime structural typing). Python's typing module includes a base class (`typing.Protocol`) to enable static structural typing (the static type stubs for tools like `collections.abc`, as well as the `@runtime_checkable` decorator, rely on `typing.Protocol`). **Within Python's static type system, Protocol is the only way to type hint duck-typed code while preserving its duck-typing nature.** It's structural typing for static analysis—the type checker verifies the object has the right shape without caring about its class.

Within Python's runtime environment, there are two ways to determine whether an object has the necessary attributes/methods for an operation:

- **Structural typing (duck typing)**: Check if an object has the necessary attributes/methods for the relevant operations (e.g., `hasattr(obj, "method")`)
- **Nominal typing**: Use an object's class name (and rules of inheritance) as a proxy for whether it has those attributes/methods (e.g., `isinstance(obj, MyClass)`)

These runtime checks are why Python is known as a "dynamically typed" language despite its technical lack of type safety as defined in type theory.  Additionally, Python's optional type hints make it a "gradually typed" language.

**CRITICAL**: If nothing else, focus on the critical use case of typing data from the edge. Your code may be sufficiently well-organized that internal static type analysis works fine without explicit declarations, but your static type checker has **no way** to assign types to untyped data received from external sources. Whenever you receive data (e.g., via a JSON file), immediately parse that information into typed structures before other operations consume it. This gives you the option of employing static type analysis throughout your codebase.

## New Adopters - Where Have You Seen This and Why Does It Matter?

If you use VSCode or PyCharm, you've already encountered type hints in action—those squiggly underlines in your code are your IDE's built-in type checker trying to help you. Don't underestimate the importance of issues that IDE developers considered critical enough to warrant visual indicators on *every relevant line of code* saying, "Hey! Pay attention to this!"

## Typing as Epistemic Resolution and Semantic Fidelity

A modest claim of this guide is that typing in Python—whether static, runtime, or hybrid—serves a deeper function than enforcing structural compatibility. Its primary value is epistemic. A typed program preserves the conceptual distinctions that constitute its domain model. While a type checker resolving a union or inferring a generic performs only structural analysis, the developer’s choice of well-formed type names establishes semantic boundaries that would otherwise collapse under Python’s dynamic runtime. A type annotation, in this sense, acts as a mechanism for maintaining the informational resolution of the program’s state space, ensuring that differences in meaning are not lost as values move through the system.

A value’s runtime representation rarely captures the conceptual category it inhabits. An integer may be encoded as an int, but the integer’s meaning within a domain is not exhausted by the operations available on that class. An int representing a user identifier, a currency amount, or a timestamp occupies different semantic roles, each with its own allowable transitions and constraints. A typed variable does not merely announce what functions can be invoked on its underlying object; it marks where that object sits in a conceptual process—its provenance, its transformation history, and the admissible operations that remain.

Consider a financial model. Whether an integer denotes U.S. dollars, British pounds, or cents after denomination conversion is often more important than its raw numeric content. Likewise, whether a value has been rounded, validated, parsed from external input, or prepared for presentation distinguishes different states in a computation. These differences can be made explicit in type markers such as USDCentsValidated or USDUnrounded, even when no separate runtime object is warranted. In Python, the construct that makes such a marker distinct to the type checker is `typing.NewType` (see *Distinct Types with `NewType`*); a plain type alias only renames. The annotation identifies the stage of a pipeline rather than its raw structure. This elevates typing from a syntactic exercise to a mechanism for tracking transitions between computational states.

This epistemic resolution becomes most valuable in function and method signatures. A well-named type, paired with well-named parameters, enables a reader to infer a function’s conceptual contract without inspecting its body. The signature signals which preconditions hold, what transformations have already occurred, and which operations the function is permitted to perform. By encoding these distinctions at the boundary, typing reduces cognitive load, prevents the inadvertent reuse of values in the wrong conceptual state, and enforces discipline in domain-driven codebases.

Note — Typing carries cognitive cost. The introduction of new types should be as disciplined as the introduction of any semantic marker (classes, domain objects, protocol boundaries). If a single well-named, more general type can accomplish the same semantic work as several more specific types, prefer the general form. Each additional type name increases cognitive load, propagates through APIs, and creates distinctions that must be remembered, maintained, and justified over time. New types should be introduced where semantic confusion is expensive, not merely where distinction is possible.

The distinction between runtime classes and static type markers follows directly from these considerations. Python treats classes as runtime types because every instance carries a pointer to its class; this nominal tag determines method dispatch and runtime behavior. A static “type,” however, is not a runtime entity but a semantic category: a constraint used by the type checker to classify values according to their conceptual roles. `NewType` declarations, Literal categories, TypeVar constraints, and other markers do not create new runtime structures. They partition the space of values for the purposes of reasoning, documentation, and static analysis. A plain type alias is the exception: it documents a role for the reader, but the checker treats it as interchangeable with the type it names. You introduce a new class when you require new runtime behavior; you introduce a new type marker whenever a value's role in the domain warrants distinction, regardless of whether the runtime representation changes.

The divide can be expressed succinctly:

* **Type Class (Runtime Entity):** A concrete constructor or primitive—`int`, `str`, `MyClass`—governing behavior at execution. It exists in memory, participates in method dispatch, and is inspected via isinstance().

* **Type Marker or Constraint (Static Category):** An abstract specification—`NewType`s, Literals, TypeVars, ParamSpecs—that classifies values for static analysis and documents their semantic role. It imposes no runtime structure and exists solely to preserve conceptual distinctions.

The remainder of this guide focuses on how these static markers operate within Python’s typing system. Throughout, it is essential to remember that Python’s dynamic runtime type is only loosely related to the semantic “type” the static type checker manipulates. In practice, developers use domain-specific type markers as conceptual scaffolding that Python’s runtime does not enforce: they use them to preserve semantic distinctions, to mark transitions between computational states, and to maintain the fidelity of a program’s domain logic over time. This account concerns how typed Python can be used to support such reasoning; it does not claim that these uses exhaust the possibilities of typing, define the aims of formal type theory, or attribute particular intentions to the designers of Python’s typing system.

## General Organization

This overview focuses primarily on the syntax of Python's type hints (as of Python 3.14), covering the contexts where developers are most likely to use or encounter them. The document is structured to facilitate both linear reading and targeted reference.

Appendices provide supplementary material, including:

- **Architectural best practices** for applying type hints effectively
- **Type hinting nomenclature and syntax** - breakdown of terminology and structure
- **Tooling ecosystem** - tools that enable and extend type hints
- **Key PEPs** - Python Enhancement Proposals governing the type system

The concluding glossary defines essential terms from type theory and typing practice. Readers are encouraged to review the glossary before consulting substantive sections to ensure clear understanding of the terminology.

**Note**: Links to relevant Python documentation are provided throughout. These may offer additional context, technical background, or expanded usage examples.  Remember that this is a non-exhaustive overview of Python's type-hinting system.  If you have questions that are not addressed herein, you might find that they are best addressed directly within the Python documentation rather than searching the web or asking AI.

## Syntax Parallels Object Declarations

A **type annotation** declares the allowed types for a name binding (specifying what types a value must have to be validly bound to that name).  Python’s type annotation syntax is intentionally aligned with Python’s object declaration syntax, creating a consistent and predictable mental model:

| Object Declaration  | Type Annotation Syntax         |
| ------------------- | ------------------------------ |
| Variables           | `name: type = value`         |
| Function parameters | `def func(param: type):`     |
| Function returns    | `def func() -> return_type:` |

To annotate names that may be bound to values of more than one static type, Python supports [union types](https://typing.python.org/en/latest/spec/concepts.html#union-types) using the `|` operator.

A long or frequently repeated type expression can be given a name with a type alias; see *Simplifying Complex Signatures with Type Aliases*.

Note: Use [`typing.reveal_type(object)`](https://typing.python.org/en/latest/spec/directives.html#reveal-type) to determine the type of an object according to the static-type checker.

The examples in this guide also use [`typing.assert_type(value, T)`](https://typing.python.org/en/latest/spec/directives.html#assert-type). It does nothing at runtime, but a type checker reports an error unless the type it infers for `value` is exactly `T`. It turns a comment such as "inferred as `list[int]`" into a claim the checker verifies.

**Collections** may also include type annotations for their elements using bracket notation following the collection type.

For **homogeneous collections** (all elements are of the same type), a single type parameter suffices:

```python
names: list[str] = ["Picard", "Riker"]
unique_ids: set[int] = {1701, 74656, 75294}
```

When a collection may hold elements of more than one type, what matters is whether the type depends on position. In a **homogeneous** collection the element type is position independent: every position has the same type, which may be a union. In a **heterogeneous** collection the type is position dependent: a tuple gives a discrete type annotation for each index position, forming a fixed schema. Note the difference between the union operator `|` for a position-independent element type and commas for positional typing in tuples.

```python
mixed_list: list[str | int] = ["hello", 42, "world"]  # Any position can be str or int
person_data: tuple[str, int, bool] = ("Picard", 65, True)  # Position 0=str, 1=int, 2=bool
```

There are, of course, more advanced contexts for typing, two of which are:

* higher order functions (functions that return functions) in general
* and wrappers (higher order functions that use Python's wrapper syntax, typically preserving the types of the wrapped function).

These are given their own sections due to the breadth of related issues.

## Type Hints Require Structural Specificity

One of the central tasks of a static analyzer is to determine whether the broadest interpretation of a provided object's type is compatible with the operation's required type signature. Sometimes this determination is straightforward—the provided object's explicitly declared type perfectly matches the operation's type signature. Other times there is Type Ambiguity: it is not immediately apparent that the provided object's type meets the operation's requirements. In practice, this ambiguity arises either because the analyzer lacks information about the object’s structure, or because the object’s known type is more general than the operation requires.

Examples of type ambiguity include:

* The provided object has a type that carries no usable structural information (epistemic ambiguity: the checker cannot prove the operation is permitted from the type alone).
* The provided object's type is a union that is too expansive (generality ambiguity: the checker cannot prove the operation is valid for all members of the union).
* The provided object's type differs from the required type (compatibility ambiguity: the checker must establish that the provided type is assignable to the required one, for example because it is a subtype or because it structurally matches a protocol).

The way a static analyzer resolves this ambiguity defines much of the system's observable behavior. In the absence of explicit type information, the analyzer may refine the type using information from control flow, assignments, and call sites, reflecting Python’s shift from purely [nominal subtyping to structural subtyping](https://docs.python.org/3/library/typing.html#nominal-vs-structural-subtyping).

Python's type hinting system is a [gradual type system](https://typing.python.org/en/latest/spec/concepts.html#static-dynamic-and-gradual-typing): it combines static and dynamic typing, and a value's type is materialized or narrowed from one type to the next as evidence becomes available. Within that system, type ambiguity takes two forms:

1. **Ambiguity from Unknown Types** (`Any`): When a function parameter lacks an annotation, or a value's type cannot be inferred, it is treated as `Any`. (An unannotated local variable usually gets a type by inference from what is assigned to it.) The analyzer therefore lacks sufficient structural information to definitively reject an operation. This ambiguity may be reduced through [materialization](https://typing.python.org/en/latest/spec/concepts.html#materialization) with a more specific type inferred from usage.
2. **Ambiguity from General Types** ([Structural Subtyping](https://typing.python.org/en/latest/spec/concepts.html#subtype-supertype-and-type-equivalence)): When the provided type is known but more general than the target usage requires. The analyzer must determine whether the type can be focused (from superset to subset) or abstracted (from subset to superset) to satisfy the operation’s constraints. Moving from an expanded set (e.g., `str | int`) to a smaller set is known as [narrowing](https://typing.python.org/en/latest/spec/narrowing.html), while moving from a specific set to a more general set is known as "widening".

Together, materialization of unknown types and narrowing or widening of general types are the forms of **type resolution**: how a type checker determines whether a value's type is permitted where it is used, updating its view of that type as evidence becomes available. *Materialization* and *narrowing* are terms from the typing specification; *type resolution* is this guide's name for the process they belong to.

This directly informs the "Robustness Principle" as applied to function signatures:

* **Input types should be as broad as possible.** (e.g., `Iterable[str]`)
* **Output types should be as narrow as possible.** (e.g., `list[str]`)

To navigate forms of ambiguity, type checkers employ several methods:

* **Type inference**: Assigning a type to an expression based on its syntactic form and operands.
* **Type resolution**: Determining whether an expression's type is permitted where it is used, updating that type as further evidence becomes available. Its forms are:
  * **Materialization**: Replacing `Any` with a more specific type (e.g., `Any` $\to$ `str` via `if isinstance(x, str)`).
  * **Narrowing**: Refining a general type to a narrower one via control flow (e.g., `float | int` $\to$ `int` via `if isinstance(x, int)`).
  * **Widening**: Treating a specific type as a wider one to satisfy an interface or expected parameter type (e.g., `list` $\to$ `Iterable`).
  * **Joining**: Combining the types of several branches or expressions into one (e.g., the type of `x if c else y`).
* **Type promotion**: Accepting an `int` where a `float` is expected, and a `float` where a `complex` is expected. This is a narrow special case in the specification (see *A Note on `int` and `float`*).

If a checker’s automatic inference or resolution is insufficiently precise, you can manually assert specificity using [`typing.cast`](https://typing.python.org/en/latest/spec/directives.html#cast).

## Related Features

The formal scope of this guide is Python’s type-hinting syntax. However, a small number of features in the typing module fall just outside that scope but are necessary for practical and semantically precise use of type hints, including constraining permitted values, declaring names that may not be rebound, and distinguishing class-level from instance-level attributes. These features are discussed toward the end of the guide.

# Python's Native Typing Support

## Standard Typing Support

In modern Python, typing support is sourced from two primary places: **built-in types** themselves and the **`typing` standard library module**. A significant simplification occurred in Python 3.9 (PEP 585), which empowered the standard built-in collection types to act as generics directly. This change established a clear best practice for developers.

## The Modern Standard: Built-in Generics

For all standard collections, the modern and preferred approach is to use the lowercase, built-in type for annotations. This is the "universal" support you will use in the vast majority of your day-to-day code.

The most common examples include:

* `list[int]`
* `dict[str, bool]`
* `set[float]`
* `tuple[int, str, int]`

This syntax is cleaner and requires no special imports.

```python
# The modern, preferred way (Python 3.9+)
def process_data(names: list[str], scores: dict[str, int]) -> None:
    for name in names:
        print(f"{name}: {scores.get(name, 'N/A')}")

# The older, legacy way
from typing import Dict, List

def process_data_legacy(names: List[str], scores: Dict[str, int]) -> None:
    # Functionally identical, but more verbose
    process_data(names, scores)
```

---

## Core Annotation Syntax

The [core syntax](https://typing.python.org/en/latest/spec/annotations.html#type-and-annotation-expressions) for applying type hints is straightforward and primarily involves three areas: annotating variables, function parameters, and function return values.

1. **Annotating variables and attributes** at the point of declaration using a colon `:`.

   ```python
   # Variable annotation
   captain: str = "Picard"

   class Starship:
       # Class attribute annotation
       registry_prefix: str = "NCC"

       def __init__(self, name: str) -> None:
           # Instance attribute annotation
           self.name: str = name
   ```
2. **Annotating function and method parameters**, also using a colon `:` after each parameter name.

   ```python
   # Each parameter is annotated after a colon.
   # ('-> None' is the return annotation, covered in the next step.)
   def rename_ship(ship: Starship, new_name: str) -> None:
       ship.name = new_name
   ```
3. **Annotating function and method return values** using an arrow `->` before the final colon of the signature.

   ```python
   # A method on Starship: the return type follows the arrow.
   def get_status_report(self) -> str:
       return f"{self.name}: Nominal."

   # A function: same syntax.
   def assign_crew(ship: Starship, crew_size: int) -> str:
       """Assigns crew and returns a confirmation message."""
       return f"{crew_size} crew assigned to the {ship.name}."
   ```

   Note: The arrow -> is read aloud as “to” when describing function return annotations (e.g., “function from int to str”). This is a pronunciation convention only; the symbol has no runtime semantics.

---

Type checkers may treat unannotated functions as having `Any` for all parameters and the return type, and may even ignore such bodies entirely. For functions you intend to be checked, it is recommended (though not required) to annotate all parameters and the return type; otherwise, missing annotations default to `Any` (except `self`/`cls`), which weakens checking unless the checker can infer something more precise.

## Type Specificity and Flexibility: Union, Any, and object

Annotations can range from highly specific to intentionally permissive.

A **Union Type**, using the pipe `|` operator, indicates that a variable can be one of several distinct types. A frequent application is handling values that could be `None`, written `str | None`. Older code spells the same type `Optional[str]`; the [typing best practices](https://typing.python.org/en/latest/reference/best_practices.html) recommend the `|` shorthand over `Union` and `Optional` wherever possible.

For situations requiring maximum flexibility, Python’s type system provides two distinct options: `object` and `Any`.

* **`object`**: The **top type**. In Python, `object` is the universal base class for all runtime values. Using it as an annotation means “this may be any object,” but the type checker will only allow operations that are valid for all objects (such as equality, identity, `str(x)`, or `repr(x)`). To perform type-specific operations, you must first narrow the value using a check such as `isinstance()`.
* **`typing.Any`**: The **escape hatch**. `Any` is a special type that disables static checking for the annotated value. It is compatible with all types, and all operations are permitted without error. This defers all type safety to runtime. Its use is discouraged because it breaks static guarantees, but it is sometimes unavoidable when interfacing with untyped libraries, dynamic data, or legacy systems.

The choice between them comes down to your reason for using them.  Use `object` when a value could be anything and you want the type checker to force proof before use. Use `Any` only when you cannot reasonably provide a type and are willing to accept the loss of static checking in that region of code.

```python
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
    # print(f"Processing object: {val.upper()}")  # ERROR: "object" has no attribute "upper"

    # CHECKER PERMITTED: To use the value, you must first prove its type.
    if isinstance(val, str):
        # Inside this block, 'val' is narrowed to 'str'.
        print(f"Processing object as string: {val.upper()}")
```

---

### Handling Names Not Yet Defined (Forward References)

A common situation arises when a type hint must refer to a name that has not yet been defined. This is known as a [forward reference](https://peps.python.org/pep-0484/#forward-references). The most frequent examples are a class method that needs to hint at the class itself, which is still in the process of being created, or to another class that appears later in the file.

In Python 3.14, the default annotation semantics (PEP 649/749) defer evaluation: annotations are stored unevaluated at definition time and are resolved only when a consumer evaluates them (for example, by reading `__annotations__` or calling `typing.get_type_hints`). This generally allows forward references to be written without quoting or reordering definitions. Caveat: forward references can still fail if annotation evaluation is triggered before all referenced names are defined. This most often happens when a wrapper evaluates annotations at definition time (for example, a decorator that calls typing.get_type_hints), or when class creation logic inspects annotations eagerly (as in some metaclasses, dataclass-like helpers, ORMs, or validation frameworks). Handling such early-evaluation patterns is out of scope here.

You will still encounter older code (targeting Python 3.13 and earlier) that relies on `from __future__ import annotations` or quotes the type name for forward references. Importing `annotations` from `__future__` in Python 3.14 opts the module into the legacy stringized-annotation model (PEP 563), disabling the new deferred-evaluation semantics introduced by PEP 649/749. By contrast, using quoted type names for forward references remains supported under deferred evaluation and does not alter the evaluation model.

```python
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

kirk = Captain("James T. Kirk", Flagship("USS Enterprise"))
```

### Simplifying Complex Signatures with Type Aliases

As type hints become more descriptive, you may find yourself reusing the same complex structure in multiple places.

```python
# This pattern might appear in several different function signatures.
def count_manifest_entries(manifest: dict[str, list[tuple[int, str]]]) -> int:
    return sum(len(records) for records in manifest.values())

def validate_crew_records(records: dict[str, list[tuple[int, str]]]) -> bool:
    return all(crew_id > 0 for crew in records.values() for crew_id, _ in crew)
```

The challenge here is not just that the definition is long, but that ensuring this exact structure is used consistently across the entire application is fragile and error-prone. A change to the pattern requires finding and updating every instance, and a typo in one can introduce a subtle inconsistency.

To address this, you can create a **type alias**, which gives a single, authoritative name to a complex type definition. This practice enforces consistency—the type is defined once and reused—and significantly improves readability by replacing a complex structure with a descriptive name.

```python
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
```

### Generic Type Aliases

The `type` statement also supports creating [generic type aliases](https://typing.python.org/en/latest/spec/generics.html#introduction).  A generic alias is a named, parameterized type expression that can be specialized with concrete types at use sites, in the same way as built-in generics such as `list[T]` or `dict[K, V]`.

Generic parameters are introduced inline as part of the alias definition, following the same syntax used for generic classes and functions.

For example, suppose you frequently work with dictionaries that map keys of some type to lists of values of that same type. You can define a reusable generic alias for this pattern:

```python
# Python 3.12+ (modern syntax)
type IDMap[K] = dict[K, list[K]]

def find_related_ids(mapping: IDMap[int], primary_id: int) -> list[int]:
    """Finds all IDs related to a primary integer ID."""
    return mapping.get(primary_id, [])

def find_related_names(mapping: IDMap[str], name: str) -> list[str]:
    """Finds all names related to a primary string name."""
    return mapping.get(name, [])

# --- Usage ---
int_relations: IDMap[int] = {101: [202, 303], 202: [101]}
related_to_101 = find_related_ids(int_relations, 101)  # list[int]

str_relations: IDMap[str] = {"riker": ["troi"], "troi": ["riker", "worf"]}
related_to_troi = find_related_names(str_relations, "troi")  # list[str]
```

Legacy Note:

Before Python 3.12, a generic alias was written `IDMap: TypeAlias = dict[K, list[K]]`, with `K = TypeVar("K")` declared separately. That form remains supported and is still required when targeting older Python versions; the difference from the modern form is purely syntactic.

Conceptual Note

Type aliases—generic or otherwise—do not create new types, either at runtime or for the checker. They give a name to a type expression so that structure and intent are stated once; the checker treats an alias and its target as the same type. A generic alias allows you to express reusable structural patterns without introducing new classes, preserving both semantic clarity and runtime simplicity.

This makes generic aliases particularly valuable for APIs and internal data flows where the shape of data matters more than its nominal class identity, and where consistency across call sites is more important than introducing new runtime objects.

### Distinct Types with `NewType`

A type alias cannot keep two values apart. If `USDCentsRaw` and `USDCentsValidated` were both aliases of `int`, the checker would treat them, and `int` itself, as one type, and passing an unvalidated amount where a validated one is required would produce no error.

When a distinction must be enforced rather than merely named, use [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype). `NewType("USDCentsValidated", int)` declares a distinct subtype of `int` that exists only for the type checker. At runtime, calling it returns its argument unchanged, so the value remains a plain `int`.

```python
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

raw = USDCentsRaw(1999)
print(post_to_ledger(validate_cents(raw)))

# The checker rejects values that skipped validation:
# post_to_ledger(raw)  # ERROR: USDCentsRaw is not USDCentsValidated
# post_to_ledger(1999)  # ERROR: a bare int is not USDCentsValidated

# No runtime wrapper: the value is still a plain int.
assert type(raw) is int
```

Because `post_to_ledger` accepts only `USDCentsValidated`, its signature states that validation has already happened. The discipline that makes this meaningful is to call `USDCentsValidated(...)` in one place, the validating function; nothing prevents another call site from wrapping an unchecked value.

```python
# By contrast, an alias is only another name for the same type.
type LooseCents = int

def post_loose(amount: LooseCents) -> str:
    return f"Posted {amount} cents"

print(post_loose(1999))  # Accepted: LooseCents and int are the same type
print(post_loose(raw))  # Accepted: nothing distinguishes the two
```

Use an alias to name or shorten a type expression. Use `NewType` when mixing two values that share an underlying type would be a bug.

# Tuples: Structured Records vs. Homogeneous Collections

The [tuple](https://typing.python.org/en/latest/spec/tuples.html) type holds a unique position in Python's typing system because it can serve two distinct purposes, and its annotation syntax reflects this duality. It can be used to describe either a **structured record** with a fixed layout or a **homogeneous, immutable sequence** of arbitrary length.

## Structured Tuples: Describing a Shape

The default way to annotate a tuple is as a structured record using the comma-separated form. This is what you use when you know the exact number of elements and the specific type of each element at its position. This makes it perfect for representing simple, heterogeneous data structures without the overhead of defining a full class.

```python
# A record containing a starship's name, class, and active status.
# The shape is fixed: a string, then another string, then a boolean.
ship_record: tuple[str, str, bool] = ("USS Enterprise", "Galaxy", True)

def process_ship_record(record: tuple[str, str, bool]) -> None:
    name, ship_class, is_active = record  # statically checked unpacking
    status = "Active" if is_active else "Inactive"
    print(f"{name} ({ship_class}): {status}")

process_ship_record(ship_record)

# The type checker flags incorrect shapes or types:
# process_ship_record(("USS Voyager", "Intrepid"))  # ERROR: missing element
# process_ship_record((1701, "Galaxy", True))  # ERROR: first element is not a str
```

## Variadic Tuples: Describing a Homogeneous Sequence

Sometimes, you don't care about a tuple's structure, only that it's an immutable sequence where every element is of the same type. For this, you use the **variadic tuple** syntax, which combines the element type with an ellipsis (`...`). The term "variadic" simply means it can accept a variable number of items.

This annotation, `tuple[SomeType, ...]`, describes a tuple of unknown length where all elements are of type `SomeType`. The typing specification calls this an *arbitrary-length homogeneous tuple*, or an *unbounded tuple*.

```python
# A collection of registry numbers of unknown length.
fleet_registry_numbers: tuple[int, ...] = (1701, 74656, 75294)

def get_smallest_ship_registry_number(registries: tuple[int, ...]) -> int:
    """Returns the smallest registry number in the collection."""
    return min(registries)

# Valid call with a tuple of integers
smallest = get_smallest_ship_registry_number((1701, 74656, 75294))

# The type checker flags this call because the elements are not all integers.
# get_smallest_ship_registry_number((1701, "NX-01"))  # ERROR: element is not an int
```

A common point of confusion is the difference between `tuple[int]` and `tuple[int, ...]`:

* `tuple[int]`: This is a **structured tuple** that must contain **exactly one** integer.
* `tuple[int, ...]`: This is a **variadic tuple** that can contain **zero or more** integers.

# Typing Collections

Most programs deal with groups of data, and Python's typing system provides a rich vocabulary for describing these collections, built on two key distinctions.

The first is between **concrete** and **abstract** types. Concrete annotations, like `list[str]` or `dict[int, float]`, are specific and describe the exact container type being used. However, for writing more flexible functions, it is often better to use abstract types that describe a collection's *capabilities* (for example, “can be iterated” or “can be indexed”). The most important of these include:

* **`Iterable`**: Any object you can loop over.
* **`Sequence`**: An ordered collection you can access by index (e.g., a `list` or `tuple`).
* **`Mapping`**: A collection that maps keys to values (e.g., a `dict`).

The second distinction is between **homogeneous** and **heterogeneous** collections. A homogeneous collection, like `list[int]`, is one where every element is expected to be of the same type. In contrast, a heterogeneous collection has a fixed layout where each position has its own specific type. The `tuple` is the primary tool for this, allowing an annotation like `tuple[str, int, bool]` to describe a record containing exactly a string, an integer, and a boolean in that precise order.

---

# Type Inference and Resolution

Beyond checking your explicit annotations, a static type checker performs **type inference**: a continuous process of accumulating constraints and maintaining an evolving approximation of each variable's possible runtime states. Annotations contribute constraints to this process; they do not enforce behavior.

**Type resolution** is the umbrella term for the operations by which a type checker updates this evolving approximation when it encounters new evidence or structural requirements. Resolution does not search for the "best" or most specific type; refinement occurs only when constraints justify eliminating possibilities. Otherwise, the checker preserves uncertainty or widens its view to satisfy an interface. Resolution is therefore a state transition process over the checker's approximation, not a preference rule over subtypes. Its two refining forms, materialization (from `Any`) and narrowing (from a wider type), are both terms from the typing specification.

Within Python's typing system, resolution occurs in several forms:

* **Implicit resolution** handles common cases without explicit intervention: merging types at branch reconvergence and accepting an `int` where a `float` is expected.
* **Conditional resolution** refines the checker's approximation based on control flow and runtime predicates. When execution enters a branch guarded by a condition, the checker eliminates states that would make that condition false. This is the mechanism behind narrowing with `isinstance`, truthiness checks, assertions, and type guards. The refinement is local to that control-flow path and is justified by reachability: execution could not have reached this point if the eliminated states were possible.
* **Structural resolution** updates the checker's approximation by matching values against structural patterns or interfaces. Pattern matching (`match`), class patterns, and protocol satisfaction partition execution into mutually exclusive cases or project a value through a structural lens. Each branch is analyzed under the assumptions introduced by the matched structure, allowing type-specific operations inside the branch without redefining the value's type outside of it.

**Type narrowing**—eliminating members from a union—is the most visible effect of resolution, but it is not the only one. Resolution may also involve materialization (replacing `Any` with a more specific type), widening (generalizing a type to satisfy an interface) and joining (merging refined approximations into a single conservative type at a reconvergence point).

Note: Type checkers differ in their inference strategies, and the exact mechanics of resolution are beyond the scope of this guide.

## Resolving to a Common Type

When a variable can be assigned values of different types, or a collection is created with heterogeneous elements, the type checker resolves this ambiguity by finding an appropriate common type, often resulting in a `Union` when the alternatives are unrelated.

Consider a conditional expression where the two possible outcomes have different types. The checker will frequently infer the variable’s type as a `Union` of both.

```python
from typing import assert_type

is_text: bool = True  # could be True or False at runtime

# The checker analyzes both branches of the conditional.
# It sees a potential 'str' and a potential 'bytes'.
data = "some text" if is_text else b"some_bytes"
assert_type(data, str | bytes)
```

For collection literals, checkers differ: pyright infers a union of the element types, while mypy joins them to their nearest common supertype, which for unrelated types is `object`.

```python
# The checker inspects each element: int, str, float.
mixed_data = [42, "answer", 6.022e23]
# Checkers disagree here. pyright infers list[int | str | float];
# mypy joins the element types and infers list[object].
# Annotate the variable when the element type matters:
measurements: list[int | str | float] = [42, "answer", 6.022e23]
```

---

### A Note on `int` and `float`

The typing specification makes one narrow special case for the built-in numeric types. `int`, `float`, and `complex` are not subtypes of one another, but a value of type `int` is accepted where a `float` is expected, and an `int` or a `float` where a `complex` is expected. Type-checker authors often call this *type promotion*; the specification lists it only as a special case for `float` and `complex`.

This is a pragmatic shortcut inherited from PEP 484, not a general mechanism. Nothing is converted at runtime, and it says nothing about the type of an arithmetic expression such as `int + float`, which comes from the declared signatures of the operators. Its exact meaning has been [under discussion in the typing community](https://discuss.python.org/t/clarifying-the-float-int-complex-special-case/54018) since 2024, so treat it as a convenience and avoid designing around it.

Note: `bool` is a subtype of `int` for type checkers, just as it is a subclass of `int` at runtime, so a `bool` is accepted wherever an `int` is expected.

```python
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
```

---

## Conditional Resolution

### The `isinstance()` Type Guard

The most explicit way to narrow a union is with `isinstance()`. When a branch is guarded by such a check, the checker refines its approximation of the variable’s type for that branch and for that branch only.  This is a control-flow effect, not a scoping effect: the variable is not redefined, only reinterpreted under additional constraints.

```python
def process_identifier(uid: str | int) -> None:
    # NOT PERMITTED: At this point the checker must account for both
    # possibilities (str and int), so a str-only method is rejected.
    # print(uid.upper())  # ERROR: "int" has no attribute "upper"

    if isinstance(uid, str):
        # CHECK PASSES: On this branch, the checker treats uid as str,
        # so str-only operations are permitted.
        print(uid.upper())

    else:
        # CHECK FAILS: On this branch, the checker treats uid as int.
        # The same str-only operation remains not permitted here.
        # print(uid.upper())  # ERROR: "int" has no attribute "upper"

        # int-specific operations are permitted instead.
        print(uid + 1000)
```

### Truthiness and None Checks

Truthiness checks are a common Python idiom, and type checkers model them as narrowing operations, especially for optional types.

```python
def get_name_length(name: str | None) -> int:
    # Runtime meaning: this branch is taken only if name is not None and not "".
    # Type-checker effect: for str | None, this eliminates None.
    if name:
        return len(name)
    else:
        return 0
```

**An explicit if name is not None check behaves similarly for narrowing `str | None`, and is often clearer because it does not also exclude falsy non-None values such as "".**

### Assertions as Proof

Sometimes you do not want to handle all members of a union. Your program’s logic may require that execution continue only if a value satisfies a specific constraint. In this case, an `assert` statement can be used to prove that constraint to the type checker.

An `assert` is a narrowing operation because it introduces a runtime check that eliminates all states in which the condition is false. Code that follows the assertion is analyzed under the constraint that the asserted condition held at runtime; if it did not, execution would have stopped. The checker therefore narrows the variable’s type by removing incompatible possibilities from further consideration.

One caveat: running Python with `-O` removes `assert` statements. Code run that way keeps the static narrowing but loses the runtime check, so an `assert` should not be the only thing validating external input.

```python
def must_be_string(uid: str | int) -> None:
    # The assertion proves to the checker that the non-str case is unreachable here.
    assert isinstance(uid, str), f"UID must be a string, but was {type(uid)}"

    # After the assertion, the checker narrows uid to str.
    print(uid.upper())
```

This is fundamentally different from `typing.cast`. An assertion proves a constraint by making violating states unreachable; a cast merely promises the checker that a constraint holds, without any runtime verification.

## Advanced Type Narrowing with Custom Guards

While `isinstance()` is powerful, its checks are limited to simple, single-type tests. For more complex validation—such as checking dictionary keys, attribute values, or structural properties—you can define your own type guard functions.  These functions tell the type checker that when the predicate returns `True`, it is allowed to treat the argument as a more specific type along that control-flow path. In this way, they serve a dual role: they perform real runtime validation, and they communicate refined type information to the type checker.

### `TypeIs`: The Modern Default for Narrowing

[typing.TypeIs](https://typing.python.org/en/latest/spec/narrowing.html#typeis) annotates a predicate that acts like a user-defined `isinstance`-style test. If it returns `True`, type checkers narrow the **first positional argument** to the target type. Unlike `TypeGuard`, the target type must be a valid refinement of the input type (i.e., it must fit within what the argument’s original type already allows). Because of that, `TypeIs` composes cleanly with prior facts and typically supports useful narrowing in the `else` branch as well (conceptually, “not T”).

Legacy Note: On some earlier Python versions, `TypeIs` may be available from the `typing_extensions` library.

```python
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

valid_roster = ["Picard", "Riker", "Data"]
log_officer_roster(valid_roster)

mixed_manifest = ("Lursa", "B'Etor", 2368)  # A tuple is a valid Sequence
log_officer_roster(mixed_manifest)
```

---

### `TypeGuard`: The Specialized Predecessor

Before `TypeIs`, there was [typing.TypeGuard](https://typing.python.org/en/latest/spec/narrowing.html#typeguard). It looks similar at the call site, but it makes a different promise: if the predicate returns `True`, the checker may treat the first positional argument **as** the specified type.

The difference is subtle but important:

`TypeIs` is for **narrowing**: it refines the checker’s existing view of a value by eliminating possibilities within the original type. That is why it can usually support narrowing in both the `if` and `else` branches.

`TypeGuard` is for **narrowing in the positive case only**: it allows the checker to adopt a new type view in the positive branch even when that view is not a clean refinement of the original type as the checker understands it (for example, where assignability relationships don’t line up neatly due to invariance or other typing constraints). Because this “as-if” view is not generally invertible, user-defined `TypeGuard` functions narrow only in the `True` case; the `else` branch retains the original type.

As a rule: prefer `TypeIs` when your predicate is a genuine refinement (the value is a member of a more specific subset of the original type). Use `TypeGuard` when the useful post-check type is best understood as an alternate type view that you only want to assume in the positive branch.

> **Note:** For a deeper exploration of how `TypeGuard` relates to `typing.cast`, see **Advanced Narrowing: Promises vs. Proof**.

---

## Structural Resolution

### Expressive Structural Narrowing with `match`

The `match` statement provides structural pattern matching that static type checkers can often use to refine their understanding of a value. The checker treats each `case` clause as a distinct control-flow branch and narrows the matched value within it.

1. **Branch-local narrowing:** Within a `case` block, the checker typically narrows the type of the matched value (and any names bound by the pattern) to the types implied by that pattern, allowing type-specific operations to be considered permitted for the duration of that block.
2. **Declared return type:** Each `return` statement is checked against the function's declared return type. Because the branches below return different types, that annotation has to be a union, and the union is what every call site sees, whichever branch actually runs.

A Note on Class Patterns:
When a case clause uses a class constructor pattern such as `case SomeClass(attr=value)`, it is called a class pattern. This form combines a type check and destructuring into a single declarative expression.

When a class pattern is evaluated, Python performs the following steps:

* Check whether the matched value is an instance of the specified class.
* If it is, bind the named attributes in the pattern to new local variables.
* Execute the code in that case block. If the value is not an instance of the class, Python continues to the next case.

This lets you express “check the type and extract its data” in one place, and static type checkers typically use the same pattern to refine the types of both the matched value and any bound variables within the branch.

```python
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

from typing import assert_type

# --- Static type check at the call site ---
some_command: Command = EngageCommand(warp_speed=9.1)
result = process_command(some_command)

# The call site sees the function's declared return type,
# whichever branch actually ran.
assert_type(result, str | float | None)
```

### A Note on Overloaded Functions

Occasionally you will encounter functions whose type-level interface is best described by several distinct call signatures. This is a form of **ad-hoc polymorphism**: the same function name is associated with several related but type-distinct entry points, each with its own argument and return types.

A generic `TypeVar` can express many parametric relationships (for example, “the return type matches the input type”), but it cannot describe genuinely distinct signatures with different constraints. The `@typing.overload` decorator exists to address this limitation. It allows you to declare multiple static call signatures for a single function so that a type checker can resolve which return type applies at a particular call site. Each overload defines a type-level contract; a single runtime implementation must be compatible with all of them.

Polymorphism in Python is more commonly expressed through **duck typing** and **Protocols**, where different objects share a common interface, rather than through ad-hoc overloading of a single function. Overloading is appropriate when an API genuinely needs several distinct, type-sensitive entry points under one name or when you must match an external library's surface. However, in ordinary application code, heavy use of overloads is often a sign that a function is handling too many cases and would be clearer as several more tightly scoped functions.

Because overloads are primarily an API-design and ergonomics concern rather than a core tool for epistemic or domain modeling, this guide does not treat them in detail.

## Advanced Narrowing: Promises vs. Proof

When a type checker cannot determine a variable’s type, you have two ways to resolve the ambiguity: you can either **promise** the checker that you know the correct type, or you can **prove** it by performing a runtime check. These correspond to `typing.cast` and type guards (`TypeIs` / `TypeGuard`).

The difference is not cosmetic. A promise changes what the checker is willing to assume. A proof changes which program states remain reachable.

---

### `typing.cast`: An Unconditional Promise

**`typing.cast`** is a direct, unconditional instruction to the type checker. It performs no runtime checks and has no runtime effect. Its only purpose is to tell the checker:

> “From this point forward, treat this value *as if* it were this other type. I am taking responsibility for that claim.”

A cast does not eliminate any possibilities; it simply replaces the checker’s current view with the one you provide. If the cast is wrong, the checker has no way to detect it, and execution proceeds anyway.

Think of it as a forged passport. You present it, and the checker accepts it without verification. This can be useful when you have knowledge the checker cannot infer, but it also means you are bypassing the checker’s normal conservatism.

---

### Type Guards: Conditional Proof

A **type guard** provides proof, but only conditionally. It performs a real **runtime check**, and its boolean result determines whether execution continues along a path where the checker is allowed to adopt a more specific type view.

If the guard returns `True`, the checker narrows the type of the guarded value in that branch. If the guard returns `False`, execution either follows a different branch or continues without refinement, depending on the kind of guard used.

This is a security checkpoint, not a forged document. The guard function actually inspects the value at runtime. Only if the check passes does execution enter the guarded region, where the checker treats the value as having satisfied the stated constraint.

* `TypeIs` narrows in **both the positive and the negative case**: the checker eliminates impossible cases in each branch.
* `TypeGuard` narrows in **the positive case only**: the checker adopts a new type view only in the positive branch, because the complement cannot be inferred safely.

In both cases, the narrowing is justified by reachability: code is only analyzed under the refined assumption because execution could not have reached that point otherwise.

---

### Side-by-Side Comparison

The following `TypedDict` key-validation example shows the practical difference. (`TypedDict` itself is introduced in the next section.)

```python
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
```

### When to Use Which

* **Use a Type Guard (`TypeIs`/`TypeGuard`)** whenever you can validate the constraint at runtime. This allows the checker to eliminate invalid possibilities and only permit the operation in branches where the constraint actually holds.
* **Use `cast`** as a tool of last resort when you have absolute certainty about a type that the checker cannot infer, and a runtime check is impossible or redundant. It signals a place where you are intentionally overriding the type system.

---

# CRITICAL USE CASE: Typing Data from the Edge

One of the most important roles of a type system is to establish a **typed boundary** where your application interfaces with the outside world. Data arriving from network APIs, JSON files, or databases is untyped from the checker’s point of view. A naive `json.loads()`, for example, produces a value that the checker can only describe as `Any` or `dict[str, Any]`, which immediately collapses static reasoning about that data.

The goal at the boundary is to **convert untyped input into a typed representation as early as possible**, so that the rest of your application can be analyzed under meaningful constraints. This limits the spread of `Any` and confines uncertainty to a small, explicit region of code.

## The Lightweight Solution: `TypedDict`

For data that is fundamentally dictionary-shaped, like most JSON objects, [typing.TypedDict](https://typing.python.org/en/latest/spec/typeddict.html) provides a lightweight way to describe expected structure. It allows you to declare which keys should exist and what types their values should have, giving the checker enough information to reason about code that consumes the data.

`TypedDict` is purely a static construct. It does not create a new runtime type, and it performs no validation. It is a declaration of *intent*, not a guarantee of correctness.

```python
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

# At the boundary, load the data and annotate it as the expected shape.
ship_data: StarshipData = json.loads(raw_json_payload)

register_ship(ship_data)
```

Because `json.loads` returns `Any`, the assignment above is accepted without structural verification. This is a **promise to the checker**, not proof that the data is valid. If the incoming data does not actually conform to `StarshipData`, the checker cannot detect that mismatch.

In production code, this pattern should be paired with **explicit runtime validation** (for example, schema validation or parsing functions that raise on invalid input) before the data is treated as typed. Typing constrains how the rest of the program is analyzed; validation determines whether the data actually deserves to be treated that way.

---

## Handling Optional Keys in `TypedDict`

Real-world data is often incomplete, and dictionaries may omit keys that are present in the type-level description. By default, all keys in a `TypedDict` are treated as **required**. To indicate that a key may be missing, you can use `typing.NotRequired`. Conversely, when the default is “all optional,” you can use `typing.Required` to mark specific keys as mandatory.

```python
from typing import NotRequired, TypedDict

class ShipHistoryData(TypedDict):
    # These keys must be present.
    name: str
    registry: str

    # This key may be missing entirely.
    commission_date: NotRequired[int]
```

From the checker’s perspective, a `NotRequired` key introduces a new source of uncertainty: the key may not exist at runtime. Checkers differ in how strictly they police this: pyright reports direct access to a key that may be absent, while mypy accepts it. Either way, the access raises `KeyError` at runtime if the key is missing, so check first.

```python
def describe_ship_history(data: ShipHistoryData) -> None:
    # Required keys can be accessed directly.
    print(f"Processing {data['name']} ({data['registry']})")

    # Check for an optional key before using it.
    if "commission_date" in data:
        # Inside this branch, the checker treats the key as present.
        print(f"Commissioned in {data['commission_date']}")
```

Using `.get()` is also common, but it narrows differently:

```python
def describe_ship_history_with_get(data: ShipHistoryData) -> None:
    commission_date = data.get("commission_date")
    if commission_date is not None:
        # Here, the checker knows the value exists and is an int.
        print(f"Commissioned in {commission_date}")
```

Both patterns are valid. The important point is that **optional keys introduce uncertainty**, and an explicit check eliminates the missing-key case before key-specific operations. This is the same narrowing mechanism you saw earlier with `T | None`, applied to dictionary shape rather than variable value.

---

## The Robust Solution: Parsing into Data Classes

While `TypedDict` is useful for describing the shape of dictionary-like data, a more robust boundary is often created by **parsing incoming data into a structured object**, such as a [dataclass](https://docs.python.org/3/library/dataclasses.html). This shifts uncertainty resolution to a single, explicit step: instead of allowing partially typed dictionaries to flow through the system, the application converts raw input into a value whose structure and invariants are enforced at construction time.

This pattern does not make the data “truer”; it makes the **uncertain states unreachable** beyond the boundary. After parsing, the rest of the application can operate under the assumption that the object’s fields exist and satisfy the class’s constraints, because execution could not have progressed otherwise.

A common way to express this boundary is a factory method (for example, `from_dict`) that takes responsibility for parsing, validation, and normalization before producing an instance.

A dataclass performs no validation of its own: constructing one directly accepts values of any type. The checks therefore have to be written in the factory, as below, or delegated to a validation library such as Pydantic (see Appendix 1).

```python
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
```

```python
raw_data = json.loads(raw_json_payload)
enterprise = StarshipRecord.from_dict(raw_data)

print(enterprise.get_status_report())
```

After this boundary, the checker no longer has to account for missing keys, wrong types, or malformed structure, because those states were eliminated during construction. This is the same principle you saw with assertions and type guards, applied at the architectural level rather than the statement level.

---

### Note on Performance

You may see [dataclasses](https://docs.python.org/3/library/dataclasses.html) defined with `@dataclass(slots=True)`. This is a runtime optimization that can significantly reduce memory usage by preventing dynamic attribute creation. Its main effect is at runtime, but a checker can use it too: mypy, for example, reports an assignment to an attribute that is not among the slots.

---

## When to Use Which

* Use **`TypedDict`** when you need a lightweight way to describe the shape of dictionary data, especially at boundaries between functions or layers where the data remains fundamentally dictionary-like.
* Use a **`dataclass` (or other class)** when the data represents a stable concept in your domain and you want to eliminate malformed states as early as possible by parsing and validation. This concentrates uncertainty at the boundary and allows the rest of the program to operate under tighter constraints.

---

# Typing Functions: Synchronous vs. Asynchronous

Python distinguishes syntactically between synchronous functions (`def`) and asynchronous functions (`async def`), but the type system does not encode this distinction as a separate kind of function object. Both are represented as [Callable](https://typing.python.org/en/latest/spec/callables.html#callable) types. The divergence appears in the return position: synchronous functions return ordinary values when called, while asynchronous functions return objects satisfying the [Awaitable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Awaitable) protocol when called, and values only when awaited.

Calling an async def function produces a coroutine object that satisfies the `Awaitable[T]` protocol and represents execution that has not started (an `async def` containing `yield` is an async generator function, covered below, and returns an async generator instead): none of the function's body has run, and the call returns to its caller immediately without involving the event loop. The body runs only when the coroutine is awaited or scheduled as a task. The awaitable therefore stands for a computation that still has to be driven, not for a value that already exists.

This design encodes the async boundary as a type-level transition rather than a categorical difference between function objects. A `def` function annotated `Callable[[int], str]` produces a `str` directly when invoked. An `async def` function annotated `Callable[[int], Awaitable[str]]` produces an `Awaitable[str]`—a computation that runs only when awaited. The outer shape remains uniform. The return type specifies whether invocation yields a value immediately, or instead yields an awaitable that must be driven to completion to obtain the value.

### Important note on return annotations

Python uses the same syntax (`-> T`) to annotate two different things, depending on context. On a function definition, the return annotation describes the value produced when the function’s computation is consumed by the language’s consumption operator. For def, consumption happens at the call site; for async def, consumption happens at the await site.

Separately, when a function is treated as a value—stored, passed, or returned—its type is described by Callable[...], and the return position of Callable describes the immediate result of invocation, not the fully consumed result. For synchronous functions these coincide; for asynchronous functions they do not.

---

## Typing Synchronous Functions and Methods

### The `Callable` Type: Describing Function Shape

Functions in Python are first-class objects. The [Callable](https://typing.python.org/en/latest/spec/callables.html) type describes their signature—the types of their parameters and their return value—without reference to implementation. The syntax is `Callable[[Arg1Type, Arg2Type, ...], ReturnType]`.

```python
from collections.abc import Callable

# 'op' accepts two integers and returns an integer
def apply_operation(a: int, b: int, op: Callable[[int, int], int]) -> int:
    return op(a, b)

# Common patterns:
# No parameters: Callable[[], str]
# No return: Callable[[str], None]
# Unchecked signature: Callable[..., Any]
```

The `...` placeholder in `Callable[..., Any]` signals that parameter types are unchecked. This is not "variadic"—it means the signature is unknown or irrelevant, typically used for decorators or when interfacing with dynamically constructed callables. The checker permits all invocations but provides no type safety for arguments.

---

### The `Never` Type: Signaling Unreachable Continuations

A function annotated to return `Never` never returns normally to its caller. It unconditionally raises an exception, terminates the process, or enters an infinite loop. This is not a behavioral constraint but a reachability guarantee: code immediately following a call to such a function is provably unreachable. (An exception it raises can still be caught by a handler in the caller.)

[typing.Never](https://typing.python.org/en/latest/spec/special-types.html#never) is an **uninhabited type**—the bottom type in the lattice. No value can inhabit it, which allows the checker to eliminate branches guarded by such calls when performing control-flow analysis. This is particularly useful for exhaustiveness checking in `match` statements and for narrowing unions when certain cases are known to be impossible.

```python
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
```

---

### The `Self` Type: Preserving Receiver Type Through Inheritance

Methods that return `self` for chaining ([fluent interfaces](https://en.wikipedia.org/wiki/Fluent_interface)) require an annotation that tracks the **most derived type** in the inheritance chain. A naïve annotation of `-> Cruiser` would force the return type to the base class, losing type information when the method is called on a subclass.

[typing.Self](https://typing.python.org/en/latest/spec/generics.html#self) resolves this by acting as an implicit type parameter bound to the receiver. When a `Battlecruiser` inherits a method annotated `-> Self`, the checker infers the return type as `Battlecruiser`, not `Cruiser`. This is not merely "the type of the current instance" but specifically the type at the point of invocation in the class hierarchy.

```python
from typing import Self

class Cruiser(Starship):
    def set_warp_speed(self, speed: int) -> Self:
        self.warp_speed = speed
        return self

class Battlecruiser(Cruiser):
    def arm_weapons(self) -> Self:
        self.weapons_armed = True
        return self

from typing import assert_type

# set_warp_speed() is defined on Cruiser, yet the chain stays a Battlecruiser.
ship = Battlecruiser("IKS Rotarran").set_warp_speed(9).arm_weapons()
assert_type(ship, Battlecruiser)
```

---

### The `@override` Decorator: Checking an Intended Override

Most type hints constrain values. The [@typing.override](https://typing.python.org/en/latest/spec/class-compat.html#override) decorator instead constrains a class definition: it asserts that a method is intended to override a method inherited from an ancestor class. If no such method exists in any ancestor, the checker raises an error.

This transforms a class of silent runtime bugs—typos in method names, signature drift during refactoring—into immediate static failures. It is particularly valuable in large codebases where the relationship between a method and its overridden counterpart may not be locally evident.

```python
from typing import override

# Starship.get_status_report() -> str is defined under "Core Annotation Syntax".
class Warbird(Starship):
    @override
    def get_status_report(self) -> str:
        return f"{self.name}: Cloaked."

    # @override
    # def get_statis_report(self) -> str:  # ERROR: no parent method has this name
    #     return "Status: Unknown"
```

At runtime the decorator only sets an `__override__` attribute on the method; it enforces nothing. Its value is in the static check it enables.

---

## Typing Asynchronous Code

This section addresses the **static vocabulary** for Python's asynchronous syntax, not the semantics of `asyncio` ([see Python's guide](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html#a-conceptual-overview-of-asyncio)) or event loop execution ([see asyncio's tasks](https://docs.python.org/3/library/asyncio-task.html)). The type system provides tools to annotate the objects produced by `async def` and the control-flow constructs that consume them, allowing checkers to reason about values crossing `await` boundaries despite non-linear execution.

---

### Coroutines and Awaitables: Deferred Computation

An `async def` function introduces a two-step computation. **Calling** the function does not execute it to completion; it returns an [**awaitable**](https://docs.python.org/3/library/asyncio-task.html#id3) that represents a computation that has not yet started. **Awaiting** that object runs it and produces the final value. Because of this, the type system distinguishes between two typing contexts: *use* and *reference*.

**Use (after `await`)**
When an async function is *used*—that is, when its result is consumed via `await`—its return annotation describes the value produced at that point. This is why an async function is written as returning `T`, not `Awaitable[T]`:

```python
import asyncio

async def fetch_ship_status(registry_id: str) -> str:
    await asyncio.sleep(0.01)
    return f"Status for {registry_id}: All systems nominal."
```

The annotation `-> str` means: *when awaited, this computation yields a string*.

**Reference (at call time)**
When an async function is *referenced*—stored, passed, or returned as a value—its type is described by `Callable[...]`, and the return position describes the result of invocation, not consumption. In this context, calling an async function produces an awaitable.

The type system provides two representations for that awaitable:

* **`Awaitable[T]`**: An abstract type for any object usable with `await` that eventually yields a value of type `T`. Prefer this in parameters and return types when the implementation is irrelevant.
* **`Coroutine[T_yield, T_send, T_return]`**: The concrete protocol implemented by [coroutine objects](https://docs.python.org/3/library/asyncio-task.html#id2) returned from `async def`. It mirrors `Generator` and exists to describe awaitables that support `.send()` and `.throw()`. Most application code does not require this specificity.

The key point is that **synchronous and asynchronous functions are both `Callable`**, but asynchronous functions return awaitables rather than immediate values. The async boundary is encoded in the *return type of invocation*, not in the function object itself.

```python
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
```

The `Coroutine` type parameters follow the same convention as `Generator`: `T_yield` and `T_send` parameterize the `.send()` protocol, while `T_return` specifies the final awaited value. For coroutines that do not use `.send()`, these are typically `Any, Any, T`. The asymmetry with `Generator` lies in how the function that produces each is annotated: a generator function's return annotation names the object the call returns (`Generator[...]`, or a supertype of it such as `Iterator[...]`), while an `async def` names only the final value, and the call returns a `Coroutine` around it. This is intentional—coroutines and generators share a protocol-level interface but differ in how control flows through them.

```python
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
# def miscounted() -> int: yield 1  # ERROR: must be Generator or one of its supertypes

from typing import assert_type

decks = count_decks(3)
assert_type(decks, Generator[int, None, str])  # exactly what was written

pending: Coroutine[Any, Any, str] = report_decks()  # a Coroutine around what was written
```

---

### Asynchronous Iterators, Iterables, and Generators

The async iteration protocol mirrors synchronous iteration. An **iterable** can be iterated over; an **iterator** yields items; a **generator** is a specific iterator produced by a generator function. The async variants introduce the same distinctions with `await` at consumption points.

* [**`AsyncIterable[T]`**](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterable): Any object usable in an `async for` loop. Analogous to `Iterable[T]`. Prefer this for function parameters when you only need to consume a stream.
* [**`AsyncIterator[T]`**](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator): An object that asynchronously yields values of type `T` one at a time. Analogous to `Iterator[T]`. Use when explicitly managing iteration state (e.g., calling `anext()`).
* [**`AsyncGenerator[T_yield, T_send]`**](https://docs.python.org/3/library/collections.abc.html#collections.abc.AsyncGenerator): The iterator returned by an `async def` function containing `yield`. Analogous to `Generator`. Use when the concrete source matters (e.g., when documenting that a function is itself an async generator rather than an arbitrary iterator).

  The `T_send` parameter in `AsyncGenerator[T_yield, T_send]` specifies what can be passed via `.asend()`, parallel to `Generator`. For async generators that do not use `.asend()`, this is typically `None`. The parameter exists to maintain protocol completeness but is rarely needed in application code.

Using these types lets you annotate asynchronous data streams with the same design discipline as synchronous code: accept the most abstract type that supports the needed operations (often `AsyncIterable[T]`), and return a more specific type only when the concrete behavior matters (for example, returning an `AsyncGenerator[...]` from a function that is itself an async generator).

---

### Creating Generic Functions with `TypeVar`

Standard abstract types like `Sequence[Any]` or `Iterable[Any]` are often insufficient because they decouple the input type from the output type. If a function accepts a list of integers and returns the first element, annotating the return as `Any` or `object` forces the caller to manually re-verify the type or proceed without any guidance from the static analyzer.

[**`TypeVar`**](https://typing.python.org/en/latest/spec/generics.html#introduction) provides a mechanism for **type correlation**. It acts as a variable within the type system that the static type checker "solves" at each call site. By using the same `TypeVar` in multiple positions, you declare a requirement of **type consistency**: the specific type bound to that variable must remain the same throughout the signature. The arguments themselves need not have identical types: where they differ, the checker solves the variable to a type that admits them all (mypy, for two unrelated types, chooses `object`).

```python
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

# --- Static Analysis Resolution ---

# The checker binds T to 'str'. The return is analyzed as 'str'.
name: str = get_first_element(["Worf", "Data"])

# The checker binds T to 'int'. The return is analyzed as 'int'.
code: int = get_first_element([1701, 74656])

# wrong: int = get_first_element(["Worf", "Data"])  # ERROR: T is str here, not int
```

Legacy Note:

Before Python 3.12, a type variable had to be created explicitly with `TypeVar` before it could be used. This form is still valid and is required when targeting older Python versions.

```python
from typing import TypeVar

T = TypeVar("T")

def get_first_element_legacy(items: Sequence[T]) -> T:
    return items[0]
```

---

# Constraining `TypeVar`: `bound` and Variance

An unconstrained `TypeVar` represents the broadest possible set of objects, which prevents the type checker from allowing any operations specific to a particular class or structure. To write generics that interact with specific object attributes, the system uses **bounds** to define the minimum required interface (nominal for classes, structural for protocols) and [**variance**](https://typing.python.org/en/latest/spec/generics.html#variance) to define how generic containers relate to one another during static analysis.

Note: when using bound, the specified type is an upper bound. Formally, if T = TypeVar("T", bound=B), then any concrete type substituted for T must satisfy T ≤ B (i.e. be a subtype of the specified supertype).

## Establishing Structural Requirements with `bound`

A [**`bound`**](https://typing.python.org/en/latest/spec/generics.html#type-variables-with-an-upper-bound) constraint establishes a mandatory supertype for the `TypeVar`. It guarantees the type checker that any concrete type provided at the call site will be a subclass of the bound class or satisfy the bound protocol. This allows the analyzer to permit access to the attributes and methods defined in that bound.

Think of it as a **type-level contract**: you are informing the checker that any type bound to this variable will always admit a specific set of operations, regardless of its concrete identity.

```python
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

from typing import assert_type

lead = first_to_report([Warbird("IRW Khazara"), Warbird("IRW Belak")])
assert_type(lead, Warbird)  # not widened to Starship

# first_to_report(["not", "ships"])  # ERROR: str does not satisfy the bound
```

## Selecting from a Closed Set with Constraints

A bound admits an open family of types: the bound itself and every subtype of it. A [**constraint**](https://typing.python.org/en/latest/spec/generics.html) list does the opposite. It restricts the type variable to a closed set of types, and the checker solves the variable to exactly one of them.

```python
# T must be solved to exactly str or exactly bytes
# (legacy spelling: T = TypeVar("T", str, bytes)).
def concatenate[T: (str, bytes)](left: T, right: T) -> T:
    return left + right

from typing import assert_type

assert_type(concatenate("NCC", "-1701"), str)
assert_type(concatenate(b"NCC", b"-1701"), bytes)

# A subclass of str is accepted, and T is solved to str itself:
assert_type(concatenate(Callsign("NCC"), Callsign("-1701")), str)

# concatenate("NCC", b"-1701")  # ERROR: str and bytes cannot be mixed
# concatenate(1701, 74656)  # ERROR: int is not one of the listed types
```

Use a bound when a function should work for a type and anything derived from it, and should preserve the specific type it was given. Use constraints when a function works for a few specific types and its arguments must agree on which one.

Note: Unlike constrained TypeVars, a bound specifies an upper bound on admissible types, rather than a closed, finite set of allowed types.

---

## Defining Relational Behavior with Variance

[Variance](https://typing.python.org/en/latest/spec/generics.html#variance) describes how a type variable behaves when it appears in input (parameter) or output (return) positions. It determines how the type checker treats subtyping relationships between generic containers—for example, whether a `list[Warbird]` can be analyzed as a `list[Starship]`.

* **Invariance (the default for `TypeVar`):** A type variable created with `TypeVar(...)` is invariant unless declared otherwise; with the bracket syntax, the checker infers variance instead (see the note after the contravariance example). Invariance prevents logical contradictions in the analysis. If the checker permitted a `list[Warbird]` to be treated as a `list[Starship]`, it would have to allow appending a `Shuttle` to it. This would violate the original constraint that the list only contains `Warbird` instances, leading to runtime failures that the type checker would be unable to predict.
* **Covariance (`covariant=True`):** Suitable for **read-only** (output) positions. If a container only yields values, the checker can safely treat a container of `Warbird` as a container of `Starship`.
* **Contravariance (`contravariant=True`):** Suitable for **write-only** (input) positions. It inverts the relationship: a `RepairScheduler[Starship]` can be safely used where a `RepairScheduler[Warbird]` is expected, because a scheduler that can handle any starship can, by definition, handle a warbird.

The invariance of `list`, and the covariance of the read-only `Sequence`, can be seen directly:

```python
from collections.abc import Sequence

warbirds: list[Warbird] = [Warbird("IRW Khazara")]

# starships: list[Starship] = warbirds  # ERROR: list is invariant
read_only: Sequence[Starship] = warbirds  # Accepted: Sequence is covariant
```

---

### Covariance

A `TypeVar` marked as **covariant** (`covariant=True`) is suitable for "output" or read-only positions. It makes the generic container's subtyping follow the type parameter's relationship: if `Warbird` is a subtype of `Starship`, then a read-only `Logbook[Warbird]` is considered a subtype of `Logbook[Starship]`. This allows a function expecting a general type to safely receive a more specific one.

```python
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

warbird_log = Logbook(Warbird("IRW Khazara"))  # Logbook[Warbird]
# Valid: The more specific log can be used where a general one is expected.
analyze_starship_log(warbird_log)
```

### Contravariance

A `TypeVar` marked as **contravariant** (`contravariant=True`) is used for "input" or write-only positions. It *inverts* the subtyping relationship: if `Warbird` is a subtype of `Starship`, then `RepairScheduler[Starship]` is a subtype of `RepairScheduler[Warbird]`. This allows a function requiring a specific type to safely receive a more general one.

```python
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

general_scheduler = RepairScheduler[Starship]()
# Valid: The more general scheduler can fulfill the role of a specific one.
service_warbird_fleet(general_scheduler, [Warbird("IRW Khazara")])
```

Note: With the class syntax introduced in Python 3.12 there is no variance keyword. The checker infers the variance of each type parameter from how it is used.

```python
# Python 3.12+ class syntax: no variance keyword. The checker infers that T is
# covariant because it only appears in output positions.
class Archive[T]:
    def __init__(self, *entries: T) -> None:
        self._entries = entries

    def latest(self) -> T:
        return self._entries[-1]

def review_archive(archive: Archive[Starship]) -> None:
    print(f"Archived: {archive.latest().get_status_report()}")

review_archive(Archive(Warbird("IRW Khazara")))  # Archive[Warbird] accepted
```

# Advanced Generic Callables: Higher-Order Functions

Higher-order functions introduce several distinct challenges for static analysis, each involving the preservation of different kinds of type relationships across callable boundaries. Python's typing system provides multiple generic mechanisms to address these challenges, but they solve orthogonal problems and should not be understood as refinements of a single pattern.

This section covers three independent typing strategies that arise when working with higher-order callables:

* **Input/output correlation using `TypeVar`**: for tracking how a single input type determines a single output type, independent of parameter structure or the number of arguments involved.
* **Positional type preservation using `TypeVarTuple` and `Unpack`**: for preserving ordered sequences of heterogeneous argument types without collapsing them into a common supertype or losing positional information.
* **Signature preservation using `ParamSpec`**: for forwarding entire callable signatures—including parameter names, defaults, positional-only and keyword-only markers—through wrappers and decorators.

Each subsection addresses a different structural inadequacy in Python's type system and can be consulted independently based on the type information your static analyzer needs to preserve.

---

## Basic Interaction of `TypeVar` with `Callable`

`TypeVar` becomes even more powerful when combined with `Callable` to describe higher-order functions. You can create new `TypeVar`s to represent different, but related, types in a single signature. This is common in functions that map, transform, or process data.

Let's define a function that takes a value of one type and a transformer function that converts it to another type. The example uses a single-argument callable for simplicity, but `TypeVar` works equally well for multi-argument callables as long as you're only tracking input-output type correlation rather than the complete parameter specification.

```python
from collections.abc import Callable

# Two type variables represent the input and output types.
def transform_value[InputType, OutputType](
    transformer: Callable[[InputType], OutputType],
    value: InputType,
) -> OutputType:
    """Applies a transformer function to a value."""
    return transformer(value)

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

# transform_value(get_ship_number, crew_size)  # ERROR: int passed where str is required
```

By using `TypeVar`, we allow the static analyzer to track a relationship between an input type and an output type and to preserve that relationship across a function boundary. As long as the callable and the value are consistent, the analyzer can propagate the inferred types without loss of information.  This is distinct from preserving full callable signatures, which is handled separately using `ParamSpec`.

However, a `TypeVar` represents a single correlated type position. When a function's behavior depends on preserving an ordered sequence of heterogeneous argument types—such as when multiple positional arguments must each retain their own distinct type identity without collapsing to a common supertype—the analyzer no longer has enough structure to preserve those correlations. In those cases, type information is either collapsed or lost entirely.

The next section introduces variadic generics, which provide the additional structure static analysis tools need to track ordered, position-dependent type relationships using `TypeVarTuple` and `Unpack`.

---

## Handling a Variable Number of Types

`TypeVar` allows static analyzers to follow types through variable-arity functions only when positional identity is not significant. It works for homogeneous `*args` (all arguments share the same type), and for cases where heterogeneous arguments are intentionally erased to a common supertype. In both cases, the analyzer does not need to remember which argument appeared in which position.

However, **when each positional argument may have a different type and that ordering must be preserved across a boundary**, a single `TypeVar` is no longer sufficient for static analysis. The analyzer needs a way to track an ordered sequence of correlated types rather than one undifferentiated type variable. That case requires variadic generics using `TypeVarTuple` and `Unpack`.

Variadic generics provide a way for static analysis tools to capture and replay a variable-length ordered sequence of types without collapsing them into a single supertype or losing positional correlation. They rely on two complementary components that work together:

* [**`TypeVarTuple`**](https://typing.python.org/en/latest/spec/generics.html#typevartuple): This is used to **collect** or capture an ordered sequence of an unknown number of types into a single "type pack."
* [**`Unpack`**](https://typing.python.org/en/latest/spec/generics.html#type-variable-tuples-must-always-be-unpacked): The unpack operation, written `*Ts` (or `Unpack[Ts]` in code that must run on Python 3.10 or earlier), is used to **distribute** the types collected by a `TypeVarTuple` into another generic type, like a `tuple` or a custom generic class.

Think of it like this: TypeVarTuple collects the concrete types of positionally dependent arguments into a single pack, and Unpack distributes that pack into another generic type, allowing a generic producer and a generic consumer to share the same positional type information.

---

## Typing Sequences Using the `*` Syntax

`*args` and `**kwargs` pose related but distinct challenges for static typing. `*args` represent a variable number of positional arguments whose individual types would otherwise be collapsed, while `**kwargs` represent a variable mapping from names to values. To handle [`*args`](https://typing.python.org/en/latest/spec/generics.html#args-as-a-type-variable-tuple), Python uses TypeVarTuple to capture the ordered sequence of positional argument types and Unpack to re-apply that sequence in another generic context, allowing type information to be shared between a generic producer and a generic consumer.

`**kwargs` are handled separately: use `ParamSpec` when forwarding an existing callable’s full signature (including its keyword parameters), and use `TypedDict` with `Unpack` when you want to constrain which keyword names are accepted and what types their values may have. In both cases, keyword arguments cannot be captured or replayed using `TypeVarTuple`.

For example, constraining keyword arguments with a `TypedDict`:

```python
from typing import Literal, NotRequired, TypedDict, Unpack

class AlertOptions(TypedDict):
    level: Literal["yellow", "red"]
    message: NotRequired[str]

def raise_alert(**kwargs: Unpack[AlertOptions]) -> str:
    message = kwargs.get("message", "no details")
    return f"{kwargs['level'].upper()} ALERT: {message}"

print(raise_alert(level="red", message="Shields down"))
print(raise_alert(level="yellow"))

# raise_alert(level="purple")  # ERROR: not one of the permitted literals
# raise_alert(severity="red")  # ERROR: unknown keyword, and 'level' is missing
```

### Capturing Type Sequences with `TypeVarTuple`

A `TypeVarTuple` acts as a placeholder for a "tuple" of types. It's the primary tool for typing functions that accept a variable number of arguments (e.g., `*args`) while preserving the individual type of each argument. By convention, its name is often plural (like `Ts`), and it is used with an asterisk (`*`) to signify that it can represent multiple types.  The `TypeVarTuple` exists only for static analysis; at runtime `*args` is just a normal tuple of values.

```python
# [*Ts] declares a TypeVarTuple (Python 3.12+): it stands for a sequence of
# types such as (str, int, bool). Legacy spelling: Ts = TypeVarTuple("Ts").
def apply_operations[*Ts](*args: *Ts) -> tuple[*Ts]:
    """
    Accepts heterogeneous positional arguments and preserves their
    individual types across the function boundary.
    """
    return args

from typing import assert_type

# The type checker solves for 'Ts' by inspecting the arguments.
# It infers that Ts = (str, int, bool)
result = apply_operations("USS Enterprise", 1701, True)
assert_type(result, tuple[str, int, bool])

ship_name = result[0]  # str
registry_num = result[1]  # int

# The analyzer can now flag incorrect usage:
# result[1].upper()  # ERROR: "int" has no attribute "upper"
# result[0] + 5  # ERROR: unsupported operand types for + ("str" and "int")
```

---

### Applying Type Sequences with `Unpack`

Once a `TypeVarTuple` has captured a pack of types, that pack must be distributed into a context that consumes individual type arguments. Generic type constructors such as `tuple[...]`, `Generic[...]`, and `Callable[...]` do not accept packed abstractions; they expect a sequence of concrete type arguments, one per generic slot (e.g., `Record[str, int, bool]`).

A `TypeVarTuple` represents a variable-length producer of type arguments, not a single argument. The `Unpack` operation is what adapts that producer to a consumer by expanding the pack into the individual type parameters the surrounding generic expects. This is why you cannot write `tuple[Ts]`: there is no single type argument to pass. Writing `tuple[*Ts]` distributes the pack so the static analyzer can align each positional type in the pack with a corresponding generic parameter.

This mechanism is what makes it possible to build generic data structures and APIs that preserve a heterogeneous, ordered sequence of types across type boundaries without collapsing or erasing positional information.

```python
# A generic class that holds a specific sequence of types.
# *Ts expands the type pack into individual type arguments.
class Record[*Ts]:
    def __init__(self, *items: *Ts) -> None:
        self._items = items

    def get_items(self) -> tuple[*Ts]:
        return self._items

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
# items[0] + 10  # ERROR: unsupported operand types for + ("str" and "int")
# items[2].upper()  # ERROR: "bool" has no attribute "upper"

# Note: Ts is a static-analysis abstraction. At runtime, Record instances
# behave like ordinary Python objects with no special type-pack handling.
```

### A Note on Syntax: `*Ts` vs. `Unpack[Ts]`

`*Ts` and `typing.Unpack[Ts]` are two spellings of one operation: expanding a captured type pack. Since Python 3.11 the star form is accepted everywhere a type pack can be expanded, including `*args: *Ts`, `tuple[*Ts]`, and `Generic[*Ts]`. Since Python 3.12 a `TypeVarTuple` can also be declared inline, as in `def apply_operations[*Ts](...)` and `class Record[*Ts]:` above.

`Unpack[Ts]` is the spelling for code that must also run on Python 3.10 or earlier, where the star form is a syntax error (there, `TypeVarTuple` and `Unpack` come from `typing_extensions`). The following class is identical in meaning to `Record`:

```python
from typing import Generic, TypeVarTuple, Unpack

LegacyTs = TypeVarTuple("LegacyTs")

# Identical in meaning to 'class Record[*Ts]' above.
class LegacyRecord(Generic[Unpack[LegacyTs]]):
    def __init__(self, *items: Unpack[LegacyTs]) -> None:
        self._items = items

    def get_items(self) -> tuple[Unpack[LegacyTs]]:
        return self._items
```

`Unpack` has one further use that has no star spelling: annotating `**kwargs` with a `TypedDict`, as shown earlier in this section.

# Advanced Generic Callables: Wrappers

Decorators are one of Python's most powerful features, allowing you to wrap a function to add new behavior like logging, timing, or caching. However, they present a significant challenge for a static type checker. A naive decorator erases the original function's signature, replacing it with a generic one that accepts any arguments and returns `Any`. This effectively creates a hole in your type safety.

```python
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

# The type checker has lost the original signature.
# It now sees 'set_course' as '(*args: Any, **kwargs: Any) -> Any',
# so this reversed call is NOT flagged.
try:
    set_course(90, "Enterprise")
except AttributeError as exc:
    # The first bad operation fails at runtime: (90).upper()
    print(f"Runtime failure: {exc}")
```

The previous sections focused on preserving positional type information for `*args`. Keyword arguments introduce a different static-analysis problem: because they are named rather than positional, they must either be structurally constrained by name, or forwarded as part of an existing callable’s parameter specification.

Preserving a function's full parameter specifications (including its positional arguments, keyword arguments, defaults, and parameter kinds) is the job of `typing.ParamSpec` and is the subject of the next section.

## Preserving Signatures with `ParamSpec`

A [**`ParamSpec`**](https://typing.python.org/en/latest/spec/generics.html#paramspec) is a special kind of type variable that stands in for the full list of parameters of a callable. It works in tandem with a regular `TypeVar` (which handles the return type) to create decorators that perfectly preserve the signature of the function they wrap.

The implementation involves three key parts:

1. Declare a `ParamSpec`, typically named `P` (`**P` in the bracket syntax; `P = ParamSpec("P")` in legacy code).
2. Declare a `TypeVar` for the return type, typically `R`.
3. The decorator accepts a `Callable[P, R]` and returns a `Callable[P, R]`. The inner `wrapper` function uses the special attributes `P.args` and `P.kwargs` so the static analyzer can preserve the original signature.

```python
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

# --- Usage Example ---

# The type checker knows the exact signature of the decorated function:
# staff_ship_class(ship_class: str, crew_size: int) -> str
confirmation: str = staff_ship_class("Galaxy", 1014)

# It also understands default arguments and return types:
# set_alert_status(status: str = "green") -> None
set_alert_status(status="red")
set_alert_status()

# Most importantly, it now catches type errors immediately:
# staff_ship_class("Sovereign", "a lot")  # ERROR: expected int, not str
# set_alert_status(1)  # ERROR: expected str, not int
```

By using `ParamSpec`, the decorator no longer erases the original signature. Static analysis tools can continue to validate calls to the decorated function using the original parameter specification and return type.

# Additional Typing Module Functionality

## The Specialist's Toolkit: The `typing` Module

While the built-in types cover concrete collections, the `typing` module remains essential for more advanced or abstract scenarios. You should reach for it when you need to describe concepts that are not themselves concrete data structures. Its primary roles are:

* **Describing Abstract Capabilities:** To make functions more flexible, you can use abstract types like **`Iterable`**, **`Sequence`**, **`Mapping`**, and **`Callable`**. These describe what an object *can do* (e.g., be looped over) rather than what it *is* (e.g., a `list`). Import these from `collections.abc`; the `typing` module's versions are deprecated aliases kept for older code.
* **Special Typing Forms:** The module provides special constructs that have no runtime equivalent but are critical for the type checker. This includes **`Any`** (the escape hatch), **`Protocol`** (for structural typing), and **`Literal`** (for specifying exact values).
* **Type Qualifiers:** **`Final`**, **`ClassVar`**, **`Required`**, and **`NotRequired`** wrap a type and say something about the annotated name itself, for example that it may not be reassigned or that a key may be absent.
* **Backwards Compatibility:** For projects that must support Python versions before 3.9, the `typing` module provides the capitalized generic types (**`List`**, **`Dict`**, **`Set`**, etc.) that were required in those older versions. **`Optional[X]`** and **`Union[X, Y]`** are likewise the older spellings of `X | None` and `X | Y`.

The guiding principle is simple: **use the built-in lowercase types (`list`, `dict`) by default. Take abstract collection types from `collections.abc`, and import from `typing` only when you need a capability that neither provides.**

## Attribute, Value, and Structural Constraints: `Literal`, `Final`,`@final`, and `ClassVar`

Beyond specifying an object's type, you can use special annotations from the `typing` module to apply more granular constraints on its value, its mutability, and its scope within a class.

### `Literal`: Restricting to Specific Values

The `Literal` type constrains a variable to a specific set of literal values. It bridges the gap between types and the actual data they represent. This is incredibly useful for things like function arguments that can only accept a few predefined string commands or status codes.

```python
from typing import Literal

# The 'mode' parameter can only be one of three specific string values.
def set_warp_drive_mode(mode: Literal["standby", "engage", "emergency"]) -> None:
    print(f"Warp drive mode set to: {mode}")

set_warp_drive_mode("engage")  # Accepted
# set_warp_drive_mode("full_speed")  # ERROR: not one of the permitted values
```

A specialized version, **`LiteralString`**, is used in security-sensitive contexts (like database queries) to require that a string is built only from literals in the source code, as far as the checker can track its derivation. That helps prevent injection attacks, but it is a static check on how the string was produced, not a guarantee about its contents.

### `Final`: Declaring Constants

The `Final` annotation indicates that a variable or attribute should not be reassigned after its initial declaration. It's the standard way to define a constant. The type checker will flag any attempt to change the value of a `Final` variable, helping to prevent accidental modification of important program constants. `Final` restricts rebinding only: the object it names can still be mutated, so a `Final` list can be appended to.

```python
from typing import Final

# MAX_WARP is a constant and should not be changed.
MAX_WARP: Final[float] = 9.975

# MAX_WARP = 10.0  # ERROR: cannot assign to a Final name

# Final forbids rebinding the name. It does not make the object immutable.
DECK_NUMBERS: Final[list[int]] = [1, 2]
DECK_NUMBERS.append(3)  # Accepted
```

#### Enforcing Design Constraints with `@final`

Inheritance is a powerful tool for extending functionality, but sometimes you need to do the opposite: you need to prevent extension to preserve the integrity of a class or method. For example, a subclass might accidentally break a critical invariant of its parent by overriding a method in an unexpected way.

The `@typing.final` decorator is a tool for communicating and enforcing this design intent. It can be used in two ways: to "seal" an entire class, preventing it from being subclassed, or to lock down a single method, preventing it from being overridden.

#### Final Classes

When applied to a class, `@final` signals that the class's design is complete and it should not be used as a base for new classes. A static type checker will raise an error if any other class attempts to inherit from a final class.

```python
from typing import final

@final
class EmergencyBroadcastSystem:
    """This system's implementation is fixed and should not be altered."""
    def send_universal_alert(self, message: str) -> None:
        print(f"ALERT: {message.upper()}")

# The type checker flags this subclass:
# class ModifiedBroadcastSystem(EmergencyBroadcastSystem):  # ERROR: cannot inherit from a final class
#     def send_universal_alert(self, message: str) -> None:
#         print("This is a modified, unauthorized alert!")
```

#### Final Methods

When applied to a method within a regular (non-final) class, `@final` prevents that specific method from being overridden by subclasses. This is useful for protecting methods that are critical to the class's internal logic and state management.

```python
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
    # def get_serial_id(self) -> str:  # ERROR: cannot override a final method
    #     return f"CLOAKED-{self._serial}"
```

Using `@final` makes your architectural decisions explicit. It helps prevent future modifications from inadvertently breaking your code's core invariants, making your codebase safer and easier to reason about, especially when designing frameworks or libraries for others to use.

### `ClassVar`: Distinguishing Class vs. Instance Attributes

Within a class, an attribute can belong either to the class itself (shared by all instances) or to each individual instance. To remove ambiguity, you can use `ClassVar` to explicitly mark a variable as a class-level attribute. This is particularly important in `dataclasses`, where any annotated attribute is assumed to be an instance field by default unless marked with `ClassVar`.

```python
from typing import ClassVar

class Runabout:
    # This attribute is shared across all Runabout instances.
    registry_prefix: ClassVar[str] = "NCC"

    def __init__(self, designation: int) -> None:
        # This is an instance attribute, unique to each object.
        self.designation: int = designation

danube = Runabout(72003)
rio_grande = Runabout(72452)

print(danube.registry_prefix)  # Prints "NCC"
print(rio_grande.registry_prefix)  # Also prints "NCC"

# A ClassVar cannot be assigned through an instance:
# danube.registry_prefix = "USS"  # ERROR: cannot assign to a class variable via an instance

Runabout.registry_prefix = "USS"  # Modifying the class var affects all instances
print(danube.registry_prefix)  # Now prints "USS"
```

---

# Appendix 1: Architectural Best Practices: Building Flexible and Robust Code

Knowing the syntax of type hinting is only the first step. Using it effectively to improve your code's architecture requires adopting a few key practices. The primary goals are to increase **flexibility**, promote **decoupling** between different parts of your application, and ensure **robustness**, especially at the boundaries where your application interacts with the outside world.

## Programming to an Interface: The Power of `Protocol`

A common mistake is to over-specify types in function signatures. For example, a function that processes a list of items might be annotated to only accept a `list`, when in reality, it would work perfectly well with a `tuple` or any other iterable object. A better approach is to "program to an interface, not an implementation." This means your functions should depend on abstract capabilities, not concrete classes.

The primary tool for this in Python is `typing.Protocol`. A protocol defines a **structural contract**—a set of methods and attributes, each with a compatible type, that an object must have to be considered a valid type for a given context. It is the type-safe version of duck typing.

By using a `Protocol`, you decouple your functions from specific data structures, making them far more reusable.

```python
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

# 4. Use the function with different, unrelated types.
freighter = Freighter("SS Xhosa", is_active=True)
warp_core = Subsystem("Warp Core", 99.8)

# Both calls are accepted because both Freighter and Subsystem
# structurally match the Reportable protocol.
print_status_report(freighter)
print_status_report(warp_core)

# An object without the required shape is rejected:
# print_status_report("just a string")  # ERROR: str is not Reportable
# print_status_report(Mislabeled())  # ERROR: right names, incompatible types
```

---

## Trust, But Verify: Runtime Type Enforcement

Static type checking is a development tool. It catches errors before you run your code, but it has a fundamental limitation: it cannot validate data coming from the outside world. When you load data from a JSON API, a database, or a user-submitted form, your static checker can't know if the data's shape and types are correct at runtime.

This is where **runtime type enforcement** libraries like **Pydantic** or **beartype** become essential. These libraries use your existing type hints to actively validate data as your program runs. If the incoming data doesn't match the expected type, they raise a clear validation error.

This practice is most critical at the **boundaries** of your application. You use these tools to parse messy, untrusted external data into clean, validated internal objects. From that point on, the rest of your application can trust the data it's working with, and the static type checker's guarantees hold true.

Here’s the `Starship` data-loading example, now made robust with Pydantic:

```python
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
```

By combining static analysis for internal logic with runtime validation at the boundaries, you create applications that are correct by design, easy to reason about, and resilient to unexpected external data.

---

# Appendix 2: Anatomy of Type Declarations and Associated Vocabulary

This addendum provides a formal breakdown of the syntax discussed in the main guide. It deconstructs Python's various type declarations into their component parts to establish a clear and consistent vocabulary.

## 1\. [Variable / Attribute Annotation](https://peps.python.org/pep-0526/)

This is the most fundamental declaration, used for local variables, instance attributes, and class attributes.

### Structure:

```
+-------------+  +----------+  +-----------+  +----------+  +-------+
|  Identifier |  |    :     |  | Type Hint |  |    =     |  | Value |
+-------------+  +----------+  +-----------+  +----------+  +-------+
       |              |              |              |            |
       |              |              |              |            +---> (Optional) The initial value assigned.
       |              |              |              +----------------> The equals sign (`=`).
       |              |              +-------------------------------> The declared type (e.g., `str`, `int`, `ClassName`).
       |              +----------------------------------------------> The colon (`:`), which introduces the annotation.
       +-------------------------------------------------------------> The name of the variable or attribute.
```

### Example:

```python
captain: str = "Picard"
```

* **Identifier**: `captain`
* **Colon**: `:`
* **Type Hint**: `str`
* **Equals sign**: `=`
* **Value**: `"Picard"`

## 2\. Function / Method Annotation

This declaration describes the types of a function's inputs and the type of its output.

### Overall Structure:

```
+-----+ +-------------+ +-----------------------------+  +----+  +---------------+  +---+
| def | |   Function  | |      Parameter List (...)   |  | -> |  |  Return Type  |  | : |
+-----+ +-------------+ +-----------------------------+  +----+  +---------------+  +---+
   |           |                     |                     |              |           |
   |           |                     |                     |              |           +-> The required colon (`:`) that terminates the signature.
   |           |                     |                     |              +-------------> The annotated type of the function's return value.
   |           |                     |                     +----------------------------> The arrow (`->`), which introduces the return annotation.
   |           |                     +--------------------------------------------------> One or more Parameter Declarations, enclosed in parentheses.
   |           +------------------------------------------------------------------------> The name of the function.
   +------------------------------------------------------------------------------------> The keyword that begins a function definition.
```

### Deconstruction of the Parameter List:

Each element within the parameter list follows the same pattern as a variable annotation.

```
( +-------------+  +----------+  +---------------+ )
  | Parameter   |  |    :     |  | Parameter Type  |
( +-------------+  +----------+  +---------------+ )
         |              |                 |
         |              |                 +---> The Type Hint for this specific parameter.
         |              +---------------------> The colon (`:`), which introduces the annotation.
         +------------------------------------> The name of the parameter.
```

### Example:

```python
def assign_crew(ship: Starship, crew_size: int) -> str:
    """Assigns crew and returns a confirmation message."""
    return f"{crew_size} crew assigned to the {ship.name}."
```

* **Function Name**: `assign_crew`
* **Parameter 1**:
  * **Identifier**: `ship`
  * **Type Hint**: `Starship`
* **Parameter 2**:
  * **Identifier**: `crew_size`
  * **Type Hint**: `int`
* **Arrow**: `->`
* **Return Type**: `str`

## 3\. Generic Type Annotation

This declaration is used for container types that hold other types.

### Structure:

```
+---------------+  +---+ +-----------------+ +---+
| Container Type|  | [ | |  Type Parameter | | ] |
+---------------+  +---+ +-----------------+ +---+
        |              |         |             |
        |              |         |             +-> The closing square bracket.
        |              |         +---------------> The type(s) contained within the generic (e.g., `int`, `str`, `T`).
        |              +-------------------------> The opening square bracket.
        +----------------------------------------> The generic container class (e.g., `list`, `dict`, `set`).
```

### Example:

```python
names: list[str] = ["Picard", "Riker"]
```

* **Container Type**: `list`
* **Type Parameter**: `str`

## 4\. [Type Alias Declaration](https://peps.python.org/pep-0695/)

This gives a new name to a complex or frequently used type hint.

### Structure:

```
+------+ +-----------+  +---+  +--------------------------+
| type | | Alias Name|  | = |  |  Complex Type Definition |
+------+ +-----------+  +---+  +--------------------------+
   |           |          |                |
   |           |          |                +-> The type being aliased (e.g., `dict[str, int]`, `tuple[str, bool]`).
   |           |          +------------------> The equals sign (`=`).
   |           +-----------------------------> The new, descriptive name for the type.
   +-----------------------------------------> The keyword that begins a type alias definition (Python 3.12+).
```

### Example:

```python
type CrewRecord = tuple[int, str]
type ShipManifest = dict[str, list[CrewRecord]]
```

* **Keyword**: `type`
* **Alias Name**: `ShipManifest`
* **Complex Type Definition**: `dict[str, list[CrewRecord]]`

## 5\. Variadic Annotations

Variadic annotations handle a variable number of items or types.

### a) Variadic Tuple

Describes a `tuple` of arbitrary length where all elements share the same type.

#### Structure:

```
+-------+  +---+ +--------------+ +-------+ +---+
| tuple |  | [ | | Element Type | | , ... | | ] |
+-------+  +---+ +--------------+ +-------+ +---+
    |          |         |            |         |
    |          |         |            |         +-> Closing bracket.
    |          |         |            +-----------> The variadic signal (`...`), representing an arbitrary-length tuple.
    |          |         +------------------------> The single type for all elements.
    |          +----------------------------------> Opening bracket.
    +--------------------------------------------> The `tuple` container type.
```

#### Example:

```python
fleet_registry_numbers: tuple[int, ...] = (1701, 74656, 75294)
```

* **Container Type**: `tuple`
* **Element Type**: `int`
* **Variadic signal**: `...`

### b) [Variadic Generic (*args*)](https://peps.python.org/pep-0646/)

Captures a variable number of arguments from a function signature, preserving the distinct type of each, into a `TypeVarTuple`.

#### Structure:

```
+-------------+  +----------+  +---+ +-----------------+
| Parameter   |  |    :     |  | * | | TypeVarTuple    |
+-------------+  +----------+  +---+ +-----------------+
       |              |          |           |
       |              |          |           +-> A `TypeVarTuple` instance (e.g., `Ts`).
       |              |          +-------------> The unpack operator (`*`): unpacks the `TypeVarTuple` into its individual types.
       |              +------------------------> The colon (`:`), which introduces the annotation.
       +--------------------------------------> The name of the `*args` parameter (e.g., `*args`).
```

#### Example:

```python
def apply_operations[*Ts](*args: *Ts) -> tuple[*Ts]:
    """
    Accepts heterogeneous positional arguments and preserves their
    individual types across the function boundary.
    """
    return args
```

* **Parameter**: `*args`
* **Unpack Operator**: `*`
* **TypeVarTuple**: `Ts`

---

# Appendix 3: The Typing Tools Ecosystem

Type hints exist in a larger ecosystem of tools that bring them to life. This appendix provides a brief orientation to the landscape, connecting the concepts in this guide to the tools you'll use to apply them.

---

## Your IDE: Where Type Checking Happens First

For most developers, the first encounter with type checking happens in their editor. Those **squiggly underlines**—typically red for errors, yellow for warnings—are a static type checker running continuously in the background as you write code.

**What those squiggles mean**: When you see a squiggly line under your code, your IDE has detected a type inconsistency. Hover over it for a description of the problem. These are the same errors you'd get from running a type checker manually, but surfaced immediately as you type.

**Common examples**:

- Red squiggle under `ship.crew_size = "many"` → assigning wrong type to an annotated attribute
- Yellow squiggle under an unused import or variable → style/quality warning
- Red squiggle under `list[int]` in Python 3.8 → using syntax not available in your configured Python version

**Connection to this guide**: Every concept discussed—from basic annotations to advanced generics—becomes actionable through these real-time checks. When you write `def process(data: str | int)` and then call `data.upper()` without narrowing, the squiggle appears immediately, teaching you why **Type Narrowing** matters.

**The major IDE integrations**:

- **VSCode** uses Pylance (Pyright) by default—this is the most common and sophisticated integration
- **PyCharm** has its own built-in type checker, generally compatible with mypy's behavior
- **Sublime Text, Vim, Emacs** can integrate mypy or Pyright through language server plugins

The feedback loop of write → squiggle → fix is how most developers learn to work with Python's type system. The command-line type checkers discussed below are the same engines, just run in batch mode for CI/CD pipelines.

---

## Static Type Checkers: Batch Analysis and CI/CD

Beyond real-time IDE checking, you'll want to run type checkers as part of your development workflow—before commits, in CI/CD pipelines, or when checking large codebases. Python has several mature options, each with different philosophies and strengths.

### [mypy](https://mypy-lang.org/)

The original and most widely adopted type checker. Developed as the reference implementation for PEP 484, mypy is what most of the Python community uses and what the typing PEPs are written against.

**Connection to this guide**: Everything discussed here is designed to work with mypy first. If you're new to type checking, start here. Its behavior defines "correct" typing in Python.

**Key characteristic**: Standards-compliant and highly configurable. You can gradually increase strictness as your project matures.

---

### [Pyright](https://github.com/microsoft/pyright)

Microsoft's type checker, written in TypeScript for exceptional performance. Powers VSCode's Python language server (Pylance).

**Connection to this guide**: Pyright has more aggressive type inference and narrowing than mypy. The **Type Narrowing** section (conditional checks, `isinstance`, `match` statements) is where you'll see the biggest differences—Pyright often infers types that mypy requires you to annotate explicitly.

**Key characteristic**: Exceptional speed makes it ideal for large codebases. If you use VSCode, you're already running it in your IDE.

---

### [Pyre](https://pyre-check.org/)

Meta's (Facebook's) type checker, designed for monorepos at massive scale.

**Connection to this guide**: Most relevant if you're working on extremely large projects (100k+ lines). Pyre includes specialized features like taint analysis for security-sensitive code that go beyond standard type checking.

**Key characteristic**: Built for enterprise scale, less common in the broader community.

---

## Runtime Validation: Enforcing Types When It Matters

Static checkers analyze code at development time, but they can't validate data arriving from the outside world. This is where runtime validation becomes essential—it's the practical implementation of the **"Typing Data from the Edge"** section.

### [Pydantic](https://docs.pydantic.dev/)

The industry standard for runtime data validation. Uses type hints to parse, validate, and serialize data.

**Connection to this guide**: Pydantic is the primary tool for making **TypedDict** patterns and **dataclass** boundaries robust. When the guide discusses parsing JSON or validating external data, Pydantic is what turns that from a best practice into a reality. It transforms your type hints into active, runtime enforcement at application boundaries.

**Key characteristic**: Powers FastAPI and is used by millions of Python developers for API validation, configuration management, and any boundary with untrusted data.

**Critical insight**: A `TypedDict` annotation is just a promise to the static checker. Pydantic's `BaseModel` actually enforces that promise at runtime.

---

### [beartype](https://github.com/beartype/beartype)

A pure runtime type checker that validates function calls against their type hints with near-zero overhead.

**Connection to this guide**: Where Pydantic is for data structures, beartype is for function contracts. Add its `@beartype` decorator to any function, and every argument and return value is validated at runtime. It's particularly useful for the **Callable** patterns and **generic functions** discussed in the guide—it ensures your carefully designed signatures are actually respected during execution.

**Key characteristic**: O(1) constant-time checking means you can leave it enabled in production without performance concerns.

---

### [typeguard](https://github.com/agronholm/typeguard)

A comprehensive runtime type checker with excellent pytest integration.

**Connection to this guide**: While beartype samples for performance, typeguard exhaustively validates everything. It's most valuable during testing, where you want to catch any deviation from your type hints, especially for complex nested structures like the **variadic generics** and **TypeVarTuple** patterns discussed in advanced sections.

**Key characteristic**: Perfect for test suites where you want maximum coverage of type constraints.

---

## Programmatic Type Checking and Automation

While IDE squiggles provide immediate feedback during development, production-grade type safety requires **automated, systematic checking** that doesn't depend on a developer noticing a visual indicator.

### Integrating Static Checkers into Your Workflow

Static type checkers should run automatically at key points in your development process:

**Pre-commit hooks**: Run `mypy` or `pyright` before allowing a commit, catching type errors before they enter version control.

**CI/CD pipelines**: Make type checking a required step in your continuous integration—if the type checker fails, the build fails.

**Pre-deployment validation**: Include type checking as part of your deployment checklist alongside tests.

This systematic approach ensures that type errors are caught regardless of whether a developer happened to notice a squiggle in their editor.

### How These Tools Work Together

The tools in this appendix aren't alternatives—they're complementary layers:

1. **IDE Integration**: Provides immediate feedback while writing code—useful for learning and quick fixes.
2. **Automated Static Checking**: Command-line type checkers (mypy/Pyright) run in CI/CD to enforce type safety systematically. This is your primary defense against type errors reaching production.
3. **Boundary Validation**: Pydantic validates data crossing into your application from APIs, files, or databases. This is the practical implementation of the "Trust, But Verify" principle discussed in **Architectural Best Practices**.
4. **Runtime Enforcement**: beartype or typeguard validate function calls during execution, acting as a safety net for the internal contracts you've defined with **Callable**, **Protocol**, and **ParamSpec**.
5. **Test-Time Validation**: Runtime checkers with pytest integration catch edge cases that slip through static analysis.

## Getting Started

If you're beginning a new project:

```bash
# Install a static checker for CI/CD
pip install mypy

# Install runtime validation for boundaries
pip install pydantic

# Run static analysis (this should be in your CI pipeline)
mypy your_package/

# Your type hints are now actively protecting your code
```

For a deeper dive into any of these tools, follow the links to their official documentation. Each tool's documentation will explain how to configure it for your specific needs, but they all consume the same type hints you've learned to write in this guide.

---

## The Big Picture

Type hints are a **specification language**. The tools in this appendix are **implementations** of that specification, each serving a different phase of the development lifecycle. Understanding when and why to use each tool is as important as understanding the type hints themselves. Automated static checking catches design errors before code is committed, runtime validation catches data errors at system boundaries, and together they transform Python from a dynamically typed language into one where you can have confidence in correctness without sacrificing flexibility.

# Appendix 4: Major Typing Enhancement Proposals (PEPs)

This section provides a chronological overview of the key PEPs that have shaped Python's typing system. Each proposal introduced a significant feature or syntax fundamental to modern type-hinting practices.

## Foundational PEPs

* **[PEP 484 - Type Hints](https://peps.python.org/pep-0484/)**: The foundational proposal that introduced the concept of type hints, the `typing` module, `TypeVar` for generics, and the `Callable` type.
* **[PEP 526 - Syntax for Variable Annotations](https://peps.python.org/pep-0526/)**: Standardized the `name: type` syntax for annotating variables and attributes, making type declarations cleaner and more consistent.

## Structural and Value Constraints

* **[PEP 544 - Protocols: Structural subtyping](https://peps.python.org/pep-0544/)**: Formalized structural ("duck") typing by introducing `typing.Protocol`, promoting more flexible and decoupled code.
* **[PEP 586 - Literal Types](https://peps.python.org/pep-0586/)**: Introduced `typing.Literal` to constrain a variable to a specific set of literal values.
* **[PEP 589 - TypedDict](https://peps.python.org/pep-0589/)**: Introduced `typing.TypedDict` to provide type hints for dictionaries with a fixed set of string keys.
* **[PEP 591 - Adding a final qualifier to typing](https://peps.python.org/pep-0591/)**: Introduced `typing.Final` to declare constants and the `@typing.final` decorator to prevent subclassing or method overriding.

## Syntactic Simplification

* **[PEP 585 - Type Hinting Generics in Standard Collections](https://peps.python.org/pep-0585/)**: Enabled the direct use of built-in collection types as generics (e.g., `list[int]` instead of `typing.List[int]`).
* **[PEP 604 - Allow writing union types as X | Y](https://peps.python.org/pep-0604/)**: Introduced the more intuitive `|` operator for creating union types (e.g., `str | int`).
* **[PEP 649 - Deferred Evaluation Of Annotations Using Descriptors](https://peps.python.org/pep-0649/)**: Made lazy evaluation of annotations the default in Python 3.14 (refined by PEP 749), so forward references no longer need quoting. This replaces, rather than adopts, the stringized model of `from __future__ import annotations` (PEP 563).

## Advanced Generics and Callables

* **[PEP 612 - Parameter Specification Variables](https://peps.python.org/pep-0612/)**: Introduced `typing.ParamSpec` to allow decorators to forward the parameter types of another callable, preserving type safety.
* **[PEP 646 - Variadic Generics](https://peps.python.org/pep-0646/)**: Introduced `typing.TypeVarTuple` and `typing.Unpack` to enable typing of functions with a variable number of differently-typed arguments (`*args`).
* **[PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)**: Introduced a more concise syntax for creating generic functions and type aliases (e.g., `def func[T](...)`).

## Type Narrowing and Method Contracts

* **[PEP 673 - Self Type](https://peps.python.org/pep-0673/)**: Introduced `typing.Self` to correctly annotate methods that return an instance of their own class.
* **[PEP 698 - Override Decorator for Static Typing](https://peps.python.org/pep-0698/)**: Introduced the `@typing.override` decorator to explicitly mark methods that are intended to override a method in a superclass.
* **[PEP 742 - TypeIs](https://peps.python.org/pep-0742/)**: Introduced `typing.TypeIs` as the preferred tool for creating user-defined type guard functions.

# Glossary of Typing Terminology

## Contravariance

A form of **variance** for "input" or write-only generic containers. It inverts the subtyping relationship: if `Warbird` is a subtype of `Starship`, then a `RepairScheduler[Starship]` is considered a valid subtype of `RepairScheduler[Warbird]`. This allows a more general type to be used where a more specific one is expected.

---

## Covariance

A form of **variance** for "output" or read-only generic containers. It allows the generic type's subtyping to follow its type parameter: if `Warbird` is a subtype of `Starship`, then a `Logbook[Warbird]` is considered a valid subtype of `Logbook[Starship]`. This allows a more specific type to be used where a more general one is expected.

---

## [Gradual Typing](https://peps.python.org/pep-0484/)

The design philosophy that allows typed and untyped code to coexist within the same codebase. This enables the incremental adoption of type hints into existing projects.

---

## Heterogeneous Collection

A collection where elements have different, position-specific types, such as `tuple[str, int]`.

---

## Homogeneous Collection

A collection where all elements are of the same type, such as `list[int]`.

---

## Invariance

The default form of **variance** for mutable generic containers like `list`. There is no subtyping relationship between instantiations of the generic; for example, `list[SubClass]` and `list[SuperClass]` are treated as completely incompatible.

---

## [Materialization](https://typing.python.org/en/latest/spec/concepts.html#materialization)

Replacing `Any` in a type with a more specific type, which makes the type more static. In the specification, a type obtained this way *is a materialization of* the original. This guide also uses the word for the checker's step of making that replacement when evidence allows, one of the forms of **Type Resolution**.

---

## Nominal Subtyping

A form of **subtyping** based on explicit inheritance. A type `B` is a nominal subtype of `A` if it is `A` itself or inherits from `A`, directly or through intermediate classes.

---

## Predicate

In a typing context, a function that returns a boolean value and is used to perform **Type Narrowing**. Functions that use [TypeIs](https://peps.python.org/pep-0742/) or `TypeGuard` are examples of predicates.

---

## [Structural Subtyping](https://peps.python.org/pep-0544/)

A form of **subtyping** based on matching structure, also known as "duck typing." A type `B` is a subtype of `A` if it has all the methods and attributes required by `A`, with compatible types, regardless of inheritance. This is enabled in Python by `typing.Protocol`.

---

## Subtyping

The principle that determines if one type can be safely used in place of another. Python's type system uses two forms: **Nominal Subtyping** (inheritance) and **Structural Subtyping** (duck typing).

---

## Type Ambiguity

A state where a static analyzer cannot yet verify that an operation is permitted for a value's type. It arises when the type is unknown (`Any`) or is known but more general than the operation requires (for example, a **Union Type**). It is reduced by **Type Resolution**.

---

## Type Narrowing

The process by which a static type checker refines its understanding of a variable's type within a specific branch of code, most commonly inside a conditional block like `if isinstance(...)`.

---

## Type Resolution

This guide's umbrella term for how a type checker, whether static or runtime, determines whether a value's type is permitted where it is used. Only execution of the code itself is indifferent to it. Its forms are **Materialization** (from `Any` to a more specific type), **Type Narrowing** (to a narrower type), widening (to a wider type), and joining (combining the types of several branches). Materialization and narrowing are terms from the typing specification; the umbrella term is not.

---

## Union Type

A type formed from a known, finite collection of other types, such as `str | int`. A value of the union belongs to at least one of them. It is a manageable constraint that can be resolved through **Type Narrowing**, whereas with `Any` the set of possibilities is unknown.

---

## [Variadic](https://peps.python.org/pep-0646/)

Refers to functions or types that accept a variable number of arguments or parameters. In Python typing, this applies to `*args` (which can be captured by a `TypeVarTuple`) and tuples of arbitrary length (annotated with `...`).

---

## Variance

Describes how subtyping relationships apply to generic types (e.g., how `list[SubClass]` relates to `list[SuperClass]`). The three kinds of variance are **Invariance**, **Covariance**, and **Contravariance**.

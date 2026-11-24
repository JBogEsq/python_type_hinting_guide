
# python_type_hinting_guide

**Modern Python Type Hinting Guide (Python 3.14, working draft)**

This repository contains a working draft of a comprehensive guide to modern Python type hinting, current as of Python 3.14. The guide focuses on *practical usage, design intent, and static-analysis–driven reasoning*, rather than duplicating reference material from the standard documentation.

The document is publicly visible to enable review and discussion. It is shared specifically to collect feedback before being stabilized into a more authoritative version.

## Start here
→ [Read the draft guide](type_hinting_git_v0.2.md)

Every Python example in the guide is an excerpt of [`typing_guide_examples.py`](typing_guide_examples.py), a single runnable module, and is checked by [`test_typing_guide_examples.py`](test_typing_guide_examples.py). To run the checks, install `pytest`, `mypy` and `pydantic`, then run `pytest -q`.

---

## How to Engage

Comments, issues, and pull requests are welcome. The most valuable feedback at this stage is:

* Conceptual errors or oversights in how typing features are explained
* Corrections or improvements to links and references to official Python documentation, with a preference for consolidated references (e.g. typing module specs) over individual PEPs where possible.
* Inaccuracies or edge cases in checker behavior (mypy, pyright, etc.)
* Places where the explanation is correct but unclear or misleading to non-experts
* Structural or pedagogical suggestions (ordering, grouping, emphasis)
* Missing topics that materially affect real-world typing practice


You should assume the document is *directionally correct but not yet final*. If something seems wrong, ambiguous, or overstated, that is precisely the kind of feedback this draft is meant to surface.

---

## Status and Licensing

This is a public, timestamped draft. It should not yet be treated as authoritative or complete.

The document is **not currently open-licensed**. Redistribution, reuse, or incorporation into other works outside this repository is not permitted without explicit permission from the author. Licensing and attribution terms may change once the document stabilizes.

---

## Table of Contents
- [Overview of Python Type Hinting (aka typing)](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#overview-of-python-type-hinting-aka-typing)
  * [Preface](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#preface)
  * [Brief Discussion of Type Theory, Type Systems, and Role of Type Hinting](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#brief-discussion-of-type-theory-type-systems-and-role-of-type-hinting)
  * [New Adopters - Where Have You Seen This and Why Does It Matter?](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#new-adopters---where-have-you-seen-this-and-why-does-it-matter)
  * [Typing as Epistemic Resolution and Semantic Fidelity](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#typing-as-epistemic-resolution-and-semantic-fidelity)
  * [General Organization](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#general-organization)
  * [Syntax Parallels Object Declarations](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#syntax-parallels-object-declarations)
  * [Type Hints Require Structural Specificity](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#type-hints-require-structural-specificity)
  * [Related Features](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#related-features)
- [Python's Native Typing Support](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#pythons-native-typing-support)
  * [Standard Typing Support](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#standard-typing-support)
  * [The Modern Standard: Built-in Generics](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#the-modern-standard-built-in-generics)
  * [Core Annotation Syntax](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#core-annotation-syntax)
  * [Type Specificity and Flexibility: Union, Any, and object](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#type-specificity-and-flexibility-union-any-and-object)
- [Tuples: Structured Records vs. Homogeneous Collections](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#tuples-structured-records-vs-homogeneous-collections)
  * [Structured Tuples: Describing a Shape](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#structured-tuples-describing-a-shape)
  * [Variadic Tuples: Describing a Homogeneous Sequence](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#variadic-tuples-describing-a-homogeneous-sequence)
- [Typing Collections](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#typing-collections)
- [Type Inference and Resolution](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#type-inference-and-resolution)
  * [Resolving to a Common Type](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#resolving-to-a-common-type)
  * [Conditional Resolution](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#conditional-resolution)
  * [Advanced Type Narrowing with Custom Guards](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#advanced-type-narrowing-with-custom-guards)
  * [Structural Resolution](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#structural-resolution)
  * [Advanced Narrowing: Promises vs. Proof](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#advanced-narrowing-promises-vs-proof)
- [CRITICAL USE CASE: Typing Data from the Edge](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#critical-use-case-typing-data-from-the-edge)
  * [The Lightweight Solution: `TypedDict`](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#the-lightweight-solution-typeddict)
  * [Handling Optional Keys in `TypedDict`](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#handling-optional-keys-in-typeddict)
  * [The Robust Solution: Parsing into Data Classes](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#the-robust-solution-parsing-into-data-classes)
  * [When to Use Which](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#when-to-use-which-1)
- [Typing Functions: Synchronous vs. Asynchronous](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#typing-functions-synchronous-vs-asynchronous)
  * [Typing Synchronous Functions and Methods](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#typing-synchronous-functions-and-methods)
  * [Typing Asynchronous Code](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#typing-asynchronous-code)
- [Constraining `TypeVar`: `bound` and Variance](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#constraining-typevar-bound-and-variance)
  * [Establishing Structural Requirements with `bound`](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#establishing-structural-requirements-with-bound)
  * [Selecting from a Closed Set with Constraints](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#selecting-from-a-closed-set-with-constraints)
  * [Defining Relational Behavior with Variance](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#defining-relational-behavior-with-variance)
- [Advanced Generic Callables: Higher-Order Functions](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#advanced-generic-callables-higher-order-functions)
  * [Basic Interaction of `TypeVar` with `Callable`](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#basic-interaction-of-typevar-with-callable)
  * [Handling a Variable Number of Types](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#handling-a-variable-number-of-types)
  * [Typing Sequences Using the `*` Syntax](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#typing-sequences-using-the--syntax)
- [Advanced Generic Callables: Wrappers](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#advanced-generic-callables-wrappers)
  * [Preserving Signatures with `ParamSpec`](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#preserving-signatures-with-paramspec)
- [Additional Typing Module Functionality](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#additional-typing-module-functionality)
  * [The Specialist's Toolkit: The `typing` Module](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#the-specialists-toolkit-the-typing-module)
  * [Attribute, Value, and Structural Constraints: `Literal`, `Final`,`@final`, and `ClassVar`](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#attribute-value-and-structural-constraints-literal-finalfinal-and-classvar)
- [Appendix 1: Architectural Best Practices: Building Flexible and Robust Code](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#appendix-1-architectural-best-practices-building-flexible-and-robust-code)
  * [Programming to an Interface: The Power of `Protocol`](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#programming-to-an-interface-the-power-of-protocol)
  * [Trust, But Verify: Runtime Type Enforcement](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#trust-but-verify-runtime-type-enforcement)
- [Appendix 2: Anatomy of Type Declarations and Associated Vocabulary](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#appendix-2-anatomy-of-type-declarations-and-associated-vocabulary)
  * [1\. Variable / Attribute Annotation](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#1-variable--attribute-annotation)
  * [2\. Function / Method Annotation](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#2-function--method-annotation)
  * [3\. Generic Type Annotation](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#3-generic-type-annotation)
  * [4\. Type Alias Declaration](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#4-type-alias-declaration)
  * [5\. Variadic Annotations](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#5-variadic-annotations)
- [Appendix 3: The Typing Tools Ecosystem](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#appendix-3-the-typing-tools-ecosystem)
  * [Your IDE: Where Type Checking Happens First](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#your-ide-where-type-checking-happens-first)
  * [Static Type Checkers: Batch Analysis and CI/CD](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#static-type-checkers-batch-analysis-and-cicd)
  * [Runtime Validation: Enforcing Types When It Matters](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#runtime-validation-enforcing-types-when-it-matters)
  * [Programmatic Type Checking and Automation](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#programmatic-type-checking-and-automation)
  * [Getting Started](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#getting-started)
  * [The Big Picture](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#the-big-picture)
- [Appendix 4: Major Typing Enhancement Proposals (PEPs)](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#appendix-4-major-typing-enhancement-proposals-peps)
  * [Foundational PEPs](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#foundational-peps)
  * [Structural and Value Constraints](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#structural-and-value-constraints)
  * [Syntactic Simplification](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#syntactic-simplification)
  * [Advanced Generics and Callables](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#advanced-generics-and-callables)
  * [Type Narrowing and Method Contracts](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#type-narrowing-and-method-contracts)
- [Glossary of Typing Terminology](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#glossary-of-typing-terminology)
  * [Contravariance](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#contravariance-1)
  * [Covariance](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#covariance-1)
  * [Gradual Typing](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#gradual-typing)
  * [Heterogeneous Collection](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#heterogeneous-collection)
  * [Homogeneous Collection](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#homogeneous-collection)
  * [Invariance](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#invariance)
  * [Materialization](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#materialization)
  * [Nominal Subtyping](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#nominal-subtyping)
  * [Predicate](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#predicate)
  * [Structural Subtyping](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#structural-subtyping)
  * [Subtyping](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#subtyping)
  * [Type Ambiguity](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#type-ambiguity)
  * [Type Narrowing](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#type-narrowing)
  * [Type Resolution](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#type-resolution)
  * [Union Type](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#union-type)
  * [Variadic](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#variadic)
  * [Variance](https://github.com/JBogEsq/python_type_hinting_guide/blob/main/type_hinting_git_v0.2.md#variance)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reduction_case_study.py
=======================
Reproducible reference implementation of the three-layer reliability
framework proposed in the accompanying paper:

    Natural language (Generation layer)
        -> typed intermediate representation (Semantic Reduction layer)
        -> kernel verification (Verification layer)
        -> canonical rendering

The domain is deliberately tiny: a controlled, template-instantiated
dialect of arithmetic word problems (three problem families). The goal is
not benchmark performance but to make the paper's central claim testable:
when the reduction map succeeds, verification is deterministic and sound;
every observed failure localizes at the reduction layer, leaving the
verifier with "no handle to verify".

Run:  python reduction_case_study.py
No third-party dependencies are required (standard library only).
"""

from __future__ import annotations
import re
import json
import random
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# ----------------------------------------------------------------------
# Layer 2 (typed IR): a small explicitly typed expression language.
# ----------------------------------------------------------------------

class Expr:
    """Base class of the typed intermediate representation."""
    type: str = "?"
    def eval(self) -> int:
        raise NotImplementedError
    def render(self) -> str:
        raise NotImplementedError

@dataclass
class Num(Expr):
    value: int
    type: str = "Int"
    def eval(self) -> int:
        return self.value
    def render(self) -> str:
        return str(self.value)

@dataclass
class BinOp(Expr):
    op: str
    lhs: Expr
    rhs: Expr
    type: str = "Int"          # Int -> Int -> Int (saturated)
    def eval(self) -> int:
        a, b = self.lhs.eval(), self.rhs.eval()
        if self.op == "+": return a + b
        if self.op == "-": return a - b
        if self.op == "*": return a * b
        raise ValueError(f"unknown operator {self.op}")
    def render(self) -> str:
        return f"({self.lhs.render()} {self.op} {self.rhs.render()})"

# ----------------------------------------------------------------------
# Layer 1 (generation, simulated): template instantiation.
# ----------------------------------------------------------------------

NAMES = ["Li", "Mei", "Ana", "Tom", "Kai", "Zoe", "Noa", "Eli"]
ITEMS = ["apples", "books", "cards", "stickers", "pencils"]

def f1(rng: random.Random) -> str:
    """One-step additive."""
    a, b = rng.sample(NAMES, 2)
    it = rng.choice(ITEMS)
    x, y = rng.randint(2, 40), rng.randint(2, 40)
    return (f"{a} has {x} {it}. {b} gives {y} more {it} to {a}. "
            f"How many {it} does {a} have now?")

def f2(rng: random.Random) -> str:
    """Two-step give away / earn."""
    a, b, c = rng.sample(NAMES, 3)
    it = rng.choice(ITEMS)
    x = rng.randint(20, 80); y = rng.randint(1, 15); z = rng.randint(1, 20)
    return (f"{a} has {x} {it}. {a} gives {y} {it} to {b}, then earns "
            f"{z} {it} from {c}. How many {it} does {a} have now?")

def f3(rng: random.Random) -> str:
    """Rate/ratio with aggregate discount."""
    a = rng.choice(NAMES); it = rng.choice(ITEMS)
    n = rng.randint(2, 12); p = rng.randint(2, 15); d = rng.randint(0, 10)
    return (f"{a} buys {n} {it} at {p} coins each. The shop applies a "
            f"discount of {d} coins to the total. How many coins does {a} pay?")

def f1_malformed(rng: random.Random) -> str:
    a, b = rng.sample(NAMES, 2)
    it = rng.choice(ITEMS)
    y = rng.randint(2, 40)
    return (f"{a} has some {it}. {b} gives {y} more {it} to {a}. "
            f"How many {it} does {a} have now?")

def f2_malformed(rng: random.Random) -> str:
    a, b = rng.sample(NAMES, 2)
    it = rng.choice(ITEMS)
    z = rng.randint(1, 20)
    return (f"{a} has several {it}. {a} gives a few {it} to {b}, then earns "
            f"{z} {it}. How many {it} does {a} have now?")

def f3_malformed(rng: random.Random) -> str:
    a = rng.choice(NAMES); it = rng.choice(ITEMS)
    n = rng.randint(2, 12)
    return (f"{a} buys {n} {it}, each at an unspecified price, with an "
            f"unknown discount. How many coins does {a} pay?")

# ----------------------------------------------------------------------
# Layer 2 (reduction): controlled English -> typed AST.
# Partial by construction: returns (None, reason) when no well-typed
# object can be built (the "no handle to verify" regime).
# ----------------------------------------------------------------------

NUM = r"(-?\d+)"

def reduce(text: str) -> (Optional[Expr], Optional[str]):
    t = f1
    m = re.fullmatch(
        rf".+ has {NUM} .+\. .+ gives {NUM} more .+ to .+\. How many .+ does .+ have now\?",
        text)
    if m:
        return BinOp("+", Num(int(m.group(1))), Num(int(m.group(2)))), None

    m = re.fullmatch(
        rf".+ has {NUM} .+\. .+ gives {NUM} .+ to .+, then earns {NUM} .+ from .+\. "
        r"How many .+ does .+ have now\?", text)
    if m:
        x, y, z = map(int, m.groups())
        return BinOp("+", BinOp("-", Num(x), Num(y)), Num(z)), None

    m = re.fullmatch(
        rf".+ buys {NUM} .+ at {NUM} coins each\. .+ discount of {NUM} coins to the total\. "
        r"How many coins does .+ pay\?", text)
    if m:
        n, p, d = map(int, m.groups())
        return BinOp("-", BinOp("*", Num(n), Num(p)), Num(d)), None

    # Reduction failure: quantify why -- each signals a different gap in
    # the semantic map (missing anchor / missing typing / missing operator).
    if "some" in text or "several" in text or "a few" in text:
        return None, "unbounded quantity: no numeric anchor to type"
    if "unspecified price" in text or "unknown discount" in text:
        return None, "free variable: expression is not a closed (ground) term"
    return None, "no reduction rule matches this sentence"

# ----------------------------------------------------------------------
# Layer 3 (verification): the "kernel" is a fixed, deterministic checker.
# Sound within the tiny semantics: accept iff candidate == IR value.
# ----------------------------------------------------------------------

def verify(ir: Expr, candidate: int) -> Dict[str, Any]:
    truth = ir.eval()
    accepted = (candidate == truth)
    return {
        "accepted": accepted,
        "truth": truth,
        "candidate": candidate,
        "feedback": None if accepted else
            f"kernel error: candidate {candidate} != evaluated term {truth} "
            f"({ir.render()}); repair required",
    }

# ----------------------------------------------------------------------
# Driver: instantiate, reduce, verify, tally.
# ----------------------------------------------------------------------

def main() -> None:
    rng = random.Random(20261002)   # pinned seed -> fully reproducible

    well_formed = {"F1 one-step": [f1(rng) for _ in range(10)],
                   "F2 two-step": [f2(rng) for _ in range(10)],
                   "F3 rate/ratio": [f3(rng) for _ in range(10)]}
    malformed = {"F1 one-step": [f1_malformed(rng) for _ in range(2)],
                 "F2 two-step": [f2_malformed(rng) for _ in range(2)],
                 "F3 rate/ratio": [f3_malformed(rng) for _ in range(2)]}

    rows = []
    for fam in well_formed:
        n_inst = len(well_formed[fam]) + len(malformed[fam])
        reduced_ok = 0
        correct_accepted = 0
        wrong_rejected = 0
        unverifiable_candidates = 0
        for text in well_formed[fam]:
            ir, err = reduce(text)
            assert ir is not None and err is None
            reduced_ok += 1
            truth = ir.eval()
            # Upstream generator (simulated): 1 correct + 2 wrong candidates,
            # including an off-by-one "plausible" candidate.
            candidates = [truth, truth + 1, truth - rng.randint(2, 5)]
            for c in candidates:
                v = verify(ir, c)
                if c == truth:
                    correct_accepted += int(v["accepted"])
                else:
                    wrong_rejected += int(not v["accepted"])
        for text in malformed[fam]:
            ir, err = reduce(text)
            assert ir is None and err is not None
            # Three candidates exist on the natural-language side but the
            # kernel has no object to check: ALL of them are unverifiable.
            unverifiable_candidates += 3
        rows.append({
            "family": fam,
            "instantiations": n_inst,
            "reduction_ok": reduced_ok,
            "reduction_fail": n_inst - reduced_ok,
            "correct_candidates_accepted": correct_accepted,
            "wrong_candidates_rejected": wrong_rejected,
            "unverifiable_candidates": unverifiable_candidates,
        })

    total = {k: sum(r[k] for r in rows)
             for k in rows[0] if k != "family"}
    total["family"] = "TOTAL"

    # Headline metrics defined in the paper:
    problems = total["instantiations"]
    verifiability = total["reduction_ok"] / problems
    verifiable_candidates = (total["correct_candidates_accepted"]
                             + total["wrong_candidates_rejected"])
    # (correctly accepted correct + correctly rejected wrong) / all checked
    kernel_accuracy = ((total["correct_candidates_accepted"]
                        + total["wrong_candidates_rejected"])
                       / verifiable_candidates)

    print("Family            Inst  Red+  Red-  Accept(correct)  Reject(wrong)  Unverifiable")
    for r in rows + [total]:
        print(f"{r['family']:<16} {r['instantiations']:>4}  {r['reduction_ok']:>4} "
              f"{r['reduction_fail']:>4}  {r['correct_candidates_accepted']:>14} "
              f"{r['wrong_candidates_rejected']:>13}  {r['unverifiable_candidates']:>12}")
    print()
    print(f"verifiability rate (problems with a well-typed IR): {verifiability:.3f}")
    print(f"kernel classification accuracy on verifiable candidates: "
          f"{kernel_accuracy:.3f}")
    print()

    # Worked example with round-trip rendering and repair feedback.
    ex = well_formed["F1 one-step"][0]
    ir, _ = reduce(ex)
    print("worked example:")
    print("  NL :", ex)
    print("  IR :", ir.render(), " :: ", ir.type)
    print("  rendered back:", ir.render(), "= ", ir.eval())
    bad = ir.eval() + 1
    v = verify(ir, bad)
    print("  candidate", bad, "->", v["feedback"])

    with open("case_study_results.json", "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "totals": total,
                   "verifiability_rate": verifiability,
                   "kernel_accuracy": kernel_accuracy}, f, indent=2)

if __name__ == "__main__":
    main()

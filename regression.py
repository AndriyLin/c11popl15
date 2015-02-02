#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import glob
import os
import subprocess
import sys

WIDTH=64
VERBOSE=False

def check(test, RF, SC, RS, ST, extra_herd_cmds=[]):
  if not test.startswith("tests"):
    test = "tests/" + test
  cmd = [ "./genmodel.py", 
          "--RF", RF,
          "--SC", SC,
          "--RS", RS,
          "--ST", ST,
          "--",
          test ] + extra_herd_cmds
  out = subprocess.check_output(cmd)
  return out

def expectFail(test, RF, SC, RS, ST, extra_herd_cmds=[]):
  _head, tail = os.path.split(test)
  print("{0} is impossible... ".format(tail).ljust(WIDTH), end="")
  out = check(test, RF, SC, RS, ST, extra_herd_cmds)
  if "No" in out: print("PASS")
  else:
    print("FAIL")
    if VERBOSE: print(out)
  if extra_herd_cmds == [] and "States 0" not in out and not "Bad executions (0 in total)" in out:
    print("POSSIBLE RACE")

def expectPass(test, RF, SC, RS, ST, extra_herd_cmds=[]):
  _head, tail = os.path.split(test)
  print("{0} is possible...    ".format(tail).ljust(WIDTH), end="")
  out = check(test, RF, SC, RS, ST, extra_herd_cmds)
  if "Ok" in out: print("PASS")
  else:
    print("FAIL")
    if VERBOSE: print(out)
  if extra_herd_cmds == [] and "States 0" not in out and not "Bad executions (0 in total)" in out:
    print("POSSIBLE RACE")

def expectRace(test, RF, SC, RS, ST, extra_herd_cmds=[]):
  _head, tail = os.path.split(test)
  print("{0} is racy...        ".format(tail).ljust(WIDTH), end="")
  out = check(test, RF, SC, RS, ST, extra_herd_cmds)
  if not "Bad executions (0 in total)" in out: print ("PASS")
  else:
    print("FAIL")
    if VERBOSE: print(out)

def setup_models(args):
  global std, naive, arfna, rseq, arf, allmodels
  std   = ("ConsRFna", "SCorig", "RSorig", "STorig", args.herdflags)
  naive = ("Naive",    "SCorig", "RSorig", "STorig", args.herdflags)
  arfna = ("Arfna",    "SCorig", "RSorig", "STorig", args.herdflags)
  rseq  = ("ConsRFna", "SCorig", "RSnew",  "STorig", args.herdflags)
  arf   = ("Arf",      "SCorig", "RSorig", "STorig", args.herdflags)
  allmodels = []
  for rf in ["ConsRFna","Naive","Arf","Arfna"]:
    for sc in ["SCorig","SCnew"]:
      for rs in ["RSorig","RSnew"]:
        for st in ["STorig","STnew"]:
          m = (rf, sc, rs, st, args.herdflags)
          allmodels.append(m)

def print_model(m):
  s = "---+ MODEL {0}_{1}_{2}_{3}".format(m[0], m[1], m[2], m[3])
  if m == std: s += " (std)"
  print(s)

def regression(args):
  ## Section 1
  ## Standard Source-to-Source Transformations are Invalid in C11
  expectPass("lb.litmus", *std)
  expectPass("cyc.litmus", *std)
  expectFail("seq.litmus", *std)
  expectPass("seq2.litmus", *std)
  
  # Section 3
  # Strengthening is Unsound
  expectFail("strengthen.litmus", *std)
  expectPass("strengthen2.litmus", *std)
  # Roach Motel Reorderings are Unsound
  expectFail("roachmotel.litmus", *std)
  expectPass("roachmotel2.litmus", *std)
  # Expression Linearisation is Unsound
  expectFail("linearisation.litmus", *std)
  expectPass("linearisation2.litmus", *std)
  
  # Section 4
  # Resolving Causality Cycles and the ConsRFna Axiom
  # Naive Fix
  expectRace("cyc_na.litmus", *naive)
  # Arfna
  if not args.skip_fig6:
    expectFail("fig6.litmus", *arfna, extra_herd_cmds=['-speedcheck', 'true'])
    expectPass("fig6_translated.litmus", *arfna, extra_herd_cmds=['-speedcheck', 'true'])
  # Strengthening the Release Sequence Definition
  expectRace("rseq_weak.litmus", *std)
  expectPass("rseq_weak2.litmus", *std)
  expectPass("rseq_weak.litmus", *rseq)
  expectPass("rseq_weak2.litmus", *rseq)
  
  if args.skip_variants:
    # Appendix A
    if args.skip_non_std_appendixA: models = [std]
    else: models = allmodels
    for m in models:
      print_model(m)
      expectPass("a1.litmus", *m)
      expectRace("a1_reorder.litmus", *m)
      expectPass("a2.litmus", *m)
      expectRace("a2_reorder.litmus", *m)
      expectPass("a3.litmus", *m)
      expectRace("a3_reorder.litmus", *m)
      expectPass("a3v2.litmus", *m)
      expectFail("a4.litmus", *m)
      expectPass("a4_reorder.litmus", *m)
      expectPass("a5.litmus", *m)
      expectRace("a5_reorder.litmus", *m)
      expectPass("a6.litmus", *m)
      expectRace("a6_reorder.litmus", *m)
      expectPass("a7.litmus", *m)
      expectRace("a7_reorder.litmus", *m)
      expectPass("a8.litmus", *m)
      expectRace("a8_reorder.litmus", *m)
      expectPass("a9.litmus", *m)
      expectRace("a9_reorder.litmus", *m)
  
    # Appendix B
    expectFail("b.litmus", *arf)
    expectPass("b_reorder.litmus", *arf)
  else:
    variants(args)
  
  # Appendix C
  expectFail("c.litmus", *arfna)
  expectRace("c_reorder.litmus", *arfna)
  expectFail("c_p.litmus", *arfna)
  expectRace("c_p_reorder.litmus", *arfna)
  expectFail("c_q.litmus", *arfna)
  expectRace("c_q_reorder.litmus", *arfna)
  expectFail("c_pq.litmus", *arfna)
  expectRace("c_pq_reorder.litmus", *arfna)

def variants(args):
  # Appendix A variants
  if args.skip_non_std_appendixA: models = [std]
  else: models = allmodels
  for m in models:
    print_model(m)
    for test in glob.glob("tests/templates/variants/a1+*"):
      expectPass(test, *std)
    for test in glob.glob("tests/templates/variants/a1_reorder+*"):
      expectRace(test, *std)
    for test in glob.glob("tests/templates/variants/a2+*"):
      expectPass(test, *std)
    for test in glob.glob("tests/templates/variants/a2_reorder+*"):
      expectRace(test, *std)
    for test in glob.glob("tests/templates/variants/a3+*"):
      expectPass(test, *std)
    for test in glob.glob("tests/templates/variants/a3_reorder+*"):
      expectRace(test, *std)
    for test in glob.glob("tests/templates/variants/a5+*"):
      expectPass(test, *std)
    for test in glob.glob("tests/templates/variants/a5_reorder+*"):
      expectRace(test, *std)
    for test in glob.glob("tests/templates/variants/a6+*"):
      expectPass(test, *std)
    for test in glob.glob("tests/templates/variants/a6_reorder+*"):
      expectRace(test, *std)
    for test in glob.glob("tests/templates/variants/a7+*"):
      expectPass(test, *std)
    for test in glob.glob("tests/templates/variants/a7_reorder+*"):
      expectRace(test, *std)

  # Appendix B variants
  for test in glob.glob("tests/templates/variants/b+*"):
    expectFail(test, *arf)
  for test in glob.glob("tests/templates/variants/b_reorder+*"):
    expectPass(test, *arf)

def main(argv=None):
  if argv is None:
    argv = sys.argv[1:]
  parser = argparse.ArgumentParser(
    description="Run model regressions"
  )
  parser.add_argument("--skip-fig6", action="store_true", help="Skip (long-running) fig6 tests")
  parser.add_argument("--skip-non-std-appendixA", action="store_true", help="Skip non-standard models for Appendix A tests")
  parser.add_argument("--skip-variants", action="store_true", help="Skip test variants")
  parser.add_argument('herdflags', nargs='*', help="Passed to herd command-line")
  args = parser.parse_args(argv)
  setup_models(args)
  regression(args)
  return 0

if __name__ == '__main__':
  sys.exit(main())

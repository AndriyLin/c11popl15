#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import glob
import sys
import subprocess

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
  print("{0} is impossible... ".format(test).ljust(WIDTH), end="")
  out = check(test, RF, SC, RS, ST, extra_herd_cmds)
  if "No" in out: print("PASS")
  else:
    print("FAIL")
    if VERBOSE: print(out)
  if extra_herd_cmds == [] and "States 0" not in out and not "Bad executions (0 in total)" in out:
    print("POSSIBLE RACE")

def expectPass(test, RF, SC, RS, ST, extra_herd_cmds=[]):
  print("{0} is possible...    ".format(test).ljust(WIDTH), end="")
  out = check(test, RF, SC, RS, ST, extra_herd_cmds)
  if "Ok" in out: print("PASS")
  else:
    print("FAIL")
    if VERBOSE: print(out)
  if extra_herd_cmds == [] and "States 0" not in out and not "Bad executions (0 in total)" in out:
    print("POSSIBLE RACE")

def expectRace(test, RF, SC, RS, ST, extra_herd_cmds=[]):
  print("{0} is racy...        ".format(test).ljust(WIDTH), end="")
  out = check(test, RF, SC, RS, ST, extra_herd_cmds)
  if not "Bad executions (0 in total)" in out: print ("PASS")
  else:
    print("FAIL")
    if VERBOSE: print(out)

def regression(args):
  ## Section 1
  ## Standard Source-to-Source Transformations are Invalid in C11
  std = ("ConsRFna", "SCorig", "RSorig", "STorig", args.herdflags)
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
  naive = ("Naive", "SCorig", "RSorig", "STorig", args.herdflags)
  expectRace("cyc_na.litmus", *naive)
  # Arfna
  if not args.skip_fig6:
    arfna = ("Arfna", "SCorig", "RSorig", "STorig", args.herdflags)
    expectFail("fig6.litmus", *arfna, extra_herd_cmds=['-speedcheck', 'true'])
    expectPass("fig6_translated.litmus", *arfna, extra_herd_cmds=['-speedcheck', 'true'])
  # Strengthening the Release Sequence Definition
  expectRace("rseq_weak.litmus", *std)
  expectPass("rseq_weak2.litmus", *std)
  rseq = ("ConsRFna", "SCorig", "RSnew", "STorig", args.herdflags)
  expectPass("rseq_weak.litmus", *rseq)
  expectPass("rseq_weak2.litmus", *rseq)
  
  # Appendix A
  # TODO: should be run over *all* models not just std
  expectPass("a1.litmus", *std)
  expectRace("a1_reorder.litmus", *std)
  expectPass("a2.litmus", *std)
  expectRace("a2_reorder.litmus", *std)
  expectPass("a3.litmus", *std)
  expectRace("a3_reorder.litmus", *std)
  expectPass("a3v2.litmus", *std)
  expectFail("a4.litmus", *std)
  expectPass("a4_reorder.litmus", *std)
  expectPass("a5.litmus", *std)
  expectRace("a5_reorder.litmus", *std)
  expectPass("a6.litmus", *std)
  expectRace("a6_reorder.litmus", *std)
  expectPass("a7.litmus", *std)
  expectRace("a7_reorder.litmus", *std)
  expectPass("a8.litmus", *std)
  expectRace("a8_reorder.litmus", *std)
  expectPass("a9.litmus", *std)
  expectRace("a9_reorder.litmus", *std)
  
  # Appendix B
  arf = ("Arf", "SCorig", "RSorig", "STorig", args.herdflags)
  expectFail("b.litmus", *arf)
  expectPass("b_reorder.litmus", *arf)
  
  # Appendix C
  arfna = ("Arfna", "SCorig", "RSorig", "STorig", args.herdflags)
  expectFail("c.litmus", *arfna)
  expectPass("c_reorder.litmus", *arfna)
  expectFail("c_p.litmus", *arfna)
  expectFail("c_q.litmus", *arfna)
  expectFail("c_pq.litmus", *arfna)
  expectPass("c_p_reorder.litmus", *arfna)
  expectPass("c_q_reorder.litmus", *arfna)
  expectPass("c_pq_reorder.litmus", *arfna)

def main(argv=None):
  if argv is None:
    argv = sys.argv[1:]
  parser = argparse.ArgumentParser(
    description="Run model regressions"
  )
  parser.add_argument("--skip-fig6", action="store_true", help="Skip (long-running) fig6 tests")
  parser.add_argument('herdflags', nargs='*', help="Passed to herd command-line")
  args = parser.parse_args(argv)
  regression(args)
  return 0

if __name__ == '__main__':
  sys.exit(main())

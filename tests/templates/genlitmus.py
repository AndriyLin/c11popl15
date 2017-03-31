#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import sys
import re
import os

# omits memory_order_consume
CHOICES_MO=[        "memory_order_seq_cst",
                    "memory_order_acq_rel",
            "memory_order_acquire", "memory_order_release",
                    "memory_order_relaxed"                  ]

def mo_short(m):
  if m == "memory_order_seq_cst": return "sc"
  if m == "memory_order_acq_rel": return "rel-acq"
  if m == "memory_order_acquire": return "acq"
  if m == "memory_order_release": return "rel"
  if m == "memory_order_relaxed": return "rlx"
  assert False

def mo_lteq(m1, m2):
  return (m1 == m2) or \
         (m1 == "memory_order_seq_cst") or \
         (m1 in [ "memory_order_acquire", "memory_order_release" ] and m2 == "memory_order_acq_rel") or \
         (m2 == "memory_order_relaxed")

def freshvar():
  freshvar.counter += 1
  return "t{0}".format(freshvar.counter)
freshvar.counter = -1


def read_accesses(regs, loc):
  """
  Deal with reads only.
  :param reg: the register string to assign to, given in code
  :param loc: the location to read from
  """
  result = []
  result.append(("Rna", regs + "*{0}".format(loc)))
  for mo in CHOICES_MO:
    if mo == "memory_order_acq_rel": continue
    tag = "R{0}".format(mo_short(mo))
    acc = regs + "atomic_load_explicit({0}, {1})".format(loc, mo)
    result.append((tag, acc))
  return result


def all_accesses(l,v,w):
  result = []
  # Writes
  result.append(("Wna", "*{0} = {1}".format(l, w)))
  for m in CHOICES_MO:
    if m == "memory_order_acq_rel": continue
    tag = "W{0}".format(mo_short(m))
    acc = "atomic_store_explicit({0}, {1}, {2})".format(l, w, m)
    result.append((tag, acc))
  # RMWs
  for msucc in CHOICES_MO:
    mfail = "memory_order_relaxed"
    tag = "C{0}".format(mo_short(msucc))
    # Previously, it seems to only generate 'zero' variable name..
    if v == "0":
      vStr = "zero"
    elif v == "1":
      vStr = "one"
    else:
      raise ValueError
    acc = "int {0} = atomic_compare_exchange_strong_explicit({1}, {2}, {3}, {4}, {5})".format(freshvar(), l, vStr, w, msucc, mfail)
    result.append((tag, acc))
  return result

READ_CHOICE_REGEX = re.compile(r"(?P<regs>[a-z0-9]*)READ_CHOICE\((?P<param>[^)]*)\)")
ACCESS_CHOICE_REGEX = re.compile(r"ACCESS_CHOICE\((?P<params>[^)]*)\)")
MO_CHOICE_REGEX = re.compile(r"MO_CHOICE\((?P<params>[^)]*)\)")

def printvariants(lines, output, out_dir, tag):
  if lines == []:
    ftag = out_dir + "/" + tag + ".litmus"
    print("Writing to {0}".format(ftag))
    f = open(ftag, "w")
    print("C {0}".format(tag), file=f)
    for l in output:
      print(l, end="", file=f)
    f.close()
    return 0
  l = lines.pop(0)
  rmatch = READ_CHOICE_REGEX.search(l)
  amatch = ACCESS_CHOICE_REGEX.search(l)
  mmatch = MO_CHOICE_REGEX.search(l)
  if rmatch:
    regs = rmatch.group("regs")
    param = rmatch.group("param")
    for t,n in read_accesses(regs, param):
      l_new = READ_CHOICE_REGEX.sub(n, l, 1)
      printvariants([l_new] + lines[:], output[:], out_dir, tag + "+" + t)
  elif amatch:
    params = amatch.group("params")
    try:
      loc,v,w = params.split(',')
    except:
      print("Error: bad ACCESS_CHOICE(l,v,w) macro at", l)
      return 1
    for t,n in all_accesses(loc,v,w):
      l_new = ACCESS_CHOICE_REGEX.sub(n, l, 1)
      printvariants([l_new] + lines[:], output[:], out_dir, tag + "+" + t)
  elif mmatch:
    params = mmatch.group("params")
    for m in params.split(","):
      m = m.strip()
      l_new = MO_CHOICE_REGEX.sub(m, l, 1)
      try:
        t = mo_short(m)
      except:
        print("Error: unrecognised memory order in MO_CHOICE macro at", l)
        return 1
      printvariants([l_new] + lines[:], output[:], out_dir, tag + "+" + t)
  else:
    output.append(l)
    printvariants(lines, output, out_dir, tag)

def main(argv=None):
  if argv is None:
    argv = sys.argv[1:]
  parser = argparse.ArgumentParser(
    description="Generate all litmus variants"
  )
  parser.add_argument("--input", required=True, type=argparse.FileType('r'), help="Template litmus file")
  parser.add_argument("--output_dir", required=True, type=str, help="Output dir")
  parser.add_argument("--output_base", required=True, type=str, help="Output base")
  args = parser.parse_args(argv)
  if not os.path.isdir(os.path.dirname(args.output_dir)):
      print("Creating directory %s." % os.path.dirname(args.output_dir))
      os.makedirs(os.path.dirname(args.output_dir))
  lines = args.input.readlines()
  return printvariants(lines, [], args.output_dir, args.output_base)

if __name__ == '__main__':
  sys.exit(main())

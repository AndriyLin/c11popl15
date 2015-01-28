#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import sys
import os

regs = [ "r{0}".format(x) for x in range(9) ]

def convert_header(header):
  for l in header:
    if l.startswith("C "): l = l.replace("C ", "C11 ")
    l = l.translate(None, "[]")
    print(l, end="")

def convert_thread_procedures(thread_procedures):
  new_procedures = []
  for procid, proc in enumerate(thread_procedures):
    new_proc = [ "P{0}".format(procid) ]
    label = "END{0}".format(procid)
    ifused = False
    for l in proc:
      l = l.strip()
      l = l.translate(None, ";")
      if l.startswith("P"): continue
      if l.strip() == "}": continue
      if "if" in l:
        reg = l.split()[1].translate(None, "()")
        l = "beq {0}, 0, {1}".format(reg, label)
        ifused = True
      l = l.replace("int ", "")
      new_proc.append(l)
    if ifused:
      new_proc.append(label + ":")
    new_procedures.append(new_proc)
  maxlines = max([ len(proc) for proc in new_procedures ])
  for i in range(maxlines):
    line = []
    for proc in new_procedures:
      pad = max([ len(l) for l in proc ])
      if i < len(proc):
        l = proc[i]
        l = l.ljust(pad, " ")
        line.append(l)
      else:
        line.append(" " * pad)
    line = " | ".join(line) + " ;"
    print(line,end="\n")

def convert(lines):
  chunks = [[]]
  for l in lines:
    if l == "\n":
      chunks.append([])
    else:
      chunks[-1].append(l)
  chunks = [ c for c in chunks if c != [] ]
  header = chunks[0]
  if "exists" in "".join(chunks[-1]):
    thread_procedures = chunks[1:-1]
    footer = chunks[-1]
  else:
    thread_procedures = chunks[1:]
    footer = ["exists (1=1)"]
  convert_header(header)
  print()
  convert_thread_procedures(thread_procedures)
  print()
  for l in footer: print(l, end="")

def main(argv=None):
  if argv is None:
    argv = sys.argv[1:]
  parser = argparse.ArgumentParser(
    description="Turn C test into mappy test"
  )
  parser.add_argument("--input", required=True, type=argparse.FileType('r'), help="Template litmus file")
  args = parser.parse_args(argv)
  lines = args.input.readlines()
  return convert(lines)

if __name__ == '__main__':
  sys.exit(main())

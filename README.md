c11popl15
=========

Translation of C11 memory model from "Common Compiler Optimisations are Invalid
in the C11 Memory Model and what we can do about it" (POPL '15)

Requirements
------------
   * python at least v2.7.3
   * herd at least X

Generating models
-----------------

Models are generated from the template [c11.cat-template] using [genmodel.py].
Model options are given at the command-line. For example,

  $ ./genmodel.py --RF Naive --SC SCnew --RS RSorig --ST STnew

generates the model (Naive, SCnew, RSorig, STnew). By default, the script will
produce (ConsRFna, SCorig, RSorig, STorig). For all options use:

  $ ./genmodel.py --help

Generating and running models
-----------------------------

All commands passed after `--` are passed automatically through to herd (which
assumes that herd is in your path). For example:

  $ ./genmodel.py --RF Arfna -- -o tmp tests/arfna.litmus

generates the model (Arfna, SCorig, RSorig, STorig) into [gen.cat] and then runs
the test arfna.litmus with the herd command:

  $ herd -conf c11.cfg -o tmp tests/arfna.litmus

The configuration file [c11.cfg] picks up the generated model.

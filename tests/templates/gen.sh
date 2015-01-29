for f in *.litmus-template; do ./genlitmus.py --input $f --output_base variants/${f/.litmus-template}; done

rm -rf ./variants/
for f in *.litmus-template; do ./genlitmus.py --input $f --output_dir ./variants/ --output_base ${f/.litmus-template}; done

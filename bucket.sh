BUCKET=c11popl15/c11

CATS=${BUCKET}/cats
mkdir -p ${CATS}

# generate all models
cp c11.cfg c11popl15/c11/cats
cp library.cat c11popl15/c11/cats
for RF in ConsRFna Naive Arf Arfna; do
  for SC in SCorig SCnew; do
    for RS in RSorig RSnew; do
      for ST in STorig STnew; do
      ./genmodel.py --RF $RF --SC $SC --RS $RS --ST $ST --output ${CATS}/${RF}_${SC}_${RS}_${ST}.cat;
      done;
    done;
  done;
done

TESTS=${BUCKET}/tests
mkdir -p ${TESTS}

cd tests
cp *.litmus ../${TESTS}
for f in *.litmus-template; do
  ./genlitmus.py --input $f --output_base ../${TESTS}/z_${f/.litmus-template};
done

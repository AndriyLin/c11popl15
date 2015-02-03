# Fixes

## Definition of sw

Definition of sw in Figure 2. should read isfence(b) rather than isfence(d) in
the last conjunct. This then matches the diagrams in Figure 3.

## a3v2

The test [a3v2.litmus] as found in the paper (in Appendix A.3) is incorrect as
it is racy. The paper lists this test as:

y = 1;          | while (!x.CAS(0,1,ACQ));
x.store(1,REL); | access(y);

which can be rephrased to elide the while loop as:

y = 1;          | r0 = x.CAS(0,1,ACQ);
x.store(1,REL); | if (r0) access(y);

however, this program is racy (on y) because there is no sw edge between the
write-release and read-acquire of x.

Since the intention of this test is to be race-free it should instead be:

y = 1;          | while (!x.CAS(1,2,ACQ)); //< changed
x.store(1,REL); | access(y);

# Clarification

## Appendix C

The expected result of this litmus test after reordering is a race.
The test, after reordering, is:

if (x.load(RLX)) {       | if (y.load(RLX))
  q.store(1,Y);          |   if (q) {
  t = p.load(X);         |     p = 1;
  if (t) y.store(1,RLX); |     x.store(1,RLX);
}                        |   }

where X and Y are any atomic or non-atomic access.

There is a race between W_Y(q,1) and R_NA(q,1). This is also the case with the
variants using CAS to replace q.store(1,Y) and p.load(X).

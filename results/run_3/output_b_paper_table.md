# Output B -- paper-ready summary table (run_3 only, not yet averaged over 3 runs)

**Note:** this is a single run. The build spec calls for averaging over 3 runs per system; that requires run_2/run_3. Reported here as run_1 point values, not means -- do not present as a stable mean in the paper without run_2/run_3.

| System | Recall | Precision | Tokens | Cost | Time (s) | Excl.hit rate | Fabrication rate |
|---|---|---|---|---|---|---|---|
| flat-RAG | 0.57 | 0.78 | 1200 | $0.0061 | 6.7 | 6% | 34% |
| 2-hop | 0.69 | 0.75 | 1522 | $0.0067 | 7.1 | 6% | 0% |
| ESG (v2) | 0.97 | 0.76 | 65334 | $0.1816 | 101.2 | 6% | 9% |

Total experiment cost (run_3, 30 questions x 3 systems): $6.81
Total wall-clock time (run_3, sum across all calls): 4024s (~67.1 min)
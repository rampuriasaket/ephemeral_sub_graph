# Output B -- paper-ready summary table (run_1 only, not yet averaged over 3 runs)

**Note:** this is a single run. The build spec calls for averaging over 3 runs per system; that requires run_2/run_3. Reported here as run_1 point values, not means -- do not present as a stable mean in the paper without run_2/run_3.

| System | Recall | Precision | Tokens | Cost | Time (s) | Excl.hit rate | Fabrication rate |
|---|---|---|---|---|---|---|---|
| flat-RAG | 0.61 | 0.81 | 1169 | $0.0058 | 10.1 | 6% | 31% |
| 2-hop | 0.73 | 0.78 | 1486 | $0.0067 | 7.2 | 6% | 0% |
| ESG (v2) | 0.97 | 0.77 | 63785 | $0.1771 | 203.7 | 6% | 9% |

Total experiment cost (run_1, 30 questions x 3 systems): $6.63
Total wall-clock time (run_1, sum across all calls): 7733s (~128.9 min)
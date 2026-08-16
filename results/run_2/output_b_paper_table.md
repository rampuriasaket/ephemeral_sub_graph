# Output B -- paper-ready summary table (run_2 only, not yet averaged over 3 runs)

**Note:** this is a single run. The build spec calls for averaging over 3 runs per system; that requires run_2/run_3. Reported here as run_1 point values, not means -- do not present as a stable mean in the paper without run_2/run_3.

| System | Recall | Precision | Tokens | Cost | Time (s) | Excl.hit rate | Fabrication rate |
|---|---|---|---|---|---|---|---|
| flat-RAG | 0.57 | 0.78 | 1172 | $0.0058 | 6.6 | 6% | 31% |
| 2-hop | 0.69 | 0.75 | 1511 | $0.0066 | 7.3 | 6% | 0% |
| ESG (v2) | 0.98 | 0.75 | 66795 | $0.1856 | 105.2 | 6% | 6% |

Total experiment cost (run_2, 30 questions x 3 systems): $6.93
Total wall-clock time (run_2, sum across all calls): 4169s (~69.5 min)
# Additional file 3: Monte Carlo scope

This supplement concerns the earlier Atlas profile audit. The spatial fractional-credit tests use exact finite-label distributions and have no Monte Carlo sampling error. The profile results below are retained results; the additional checks dated 28 October 2026 are post-result validation and do not replace the frozen analyses or their criteria.

The retained panel mean-statistic tests used 9,999 null draws and the plus-one estimate (exceedances + 1)/10,000. The AVI missense consequence-matched, context-weighted comparison, its analysis excluding the chr13 genes, and the three other-intronic splicing comparisons each had zero exceedances. Their raw reported p-value was therefore 0.0001, the simulation resolution floor. The recorded plug-in Monte Carlo standard error was 0.0001; this is an estimated precision diagnostic, not a known true standard error at a zero-exceedance boundary. The corresponding recorded Wilson interval for the exceedance probability, mapped through the plus-one formula, was [0.000100, 0.000484]. These intervals describe Monte Carlo precision conditional on the fitted label model, not uncertainty in biological effects.

| Family and Euclidean scorer | Sites | Exceedances / draws | Reported raw p | Reported BH q |
|---|---:|---:|---:|---:|
| Missense, consequence matched and context weighted: AVI | 246 | 0 / 9,999 | 0.0001 | 0.00132 |
| Same analysis excluding chr13 genes: AVI | 170 | 0 / 9,999 | 0.0001 | 0.00165 |
| Other intronic, context weighted: splice junctions | 63 | 0 / 9,999 | 0.0001 | 0.000252 |
| Other intronic, context weighted: splice sites | 63 | 0 / 9,999 | 0.0001 | 0.000252 |
| Other intronic, context weighted: splice-site usage | 63 | 0 / 9,999 | 0.0001 | 0.000252 |

For AVI, these Euclidean rankings compare each alternate profile's distance from the declared background profile. They are not rankings of the raw AVI value. The mean statistic subtracts the larger of the two unselected distances from the selected distance, then averages over sites. Both highlighted missense means are negative even though they exceed the means under their specified label nulls:

| Consequence-matched, context-weighted AVI Euclidean comparison | Observed mean selected-minus-largest-other distance | Simulated null mean | Observed minus simulated null mean |
|---|---:|---:|---:|
| All 246 missense positions | -0.012798807 | -0.082914582 | 0.070115775 |
| The 170 missense positions outside chr13 genes | -0.040677371 | -0.078455404 | 0.037778033 |

The simulated null means average 9,999 draws; they are not exact conditional expectations. Significant enrichment here means a shift relative to that specified null, not a positive average margin over the strongest alternative. Source: retained `results/sensitivity/panel_within_site.json`, `/families/primary|missense_matched_ctx/rows` and `/families/primary_nochr13|missense_matched_ctx/rows`, each selecting the unique row with `scorer = AVI_SCORE` and `geometry = euclidean`; the columns are `statistic`, `null_mean` and `excess_over_null`. These values also appear in `independent_math_results.json` under `/historical_uncertainty/rows/0` and `/historical_uncertainty/rows/1`.

The adjusted q-values are point estimates computed jointly within their stated families. A raw-p standard error is not an adjusted-q standard error. The printed q-values should not be interpreted as having exact precision to every displayed digit. The exploratory CONTACT_MAPS top-1 result, q = 0.0441, comes from a binomial test and does not use the Monte Carlo mean-statistic calculation.

The frozen coding analysis reported 37 significant uniform-null comparisons and 10 consequence-matched comparisons. Its planned criterion was at most one quarter as many matched as uniform significant comparisons; 10 exceeds 37/4, so that criterion was not met. Three further independent random-number streams, each using 9,999 draws and the unchanged statistics, sites, families and threshold, again produced 37 and 10. These redraws assess Monte Carlo seed sensitivity and do not alter the original result.

A separate conservative check enclosed all 132 underlying exceedance probabilities simultaneously using Bonferroni-adjusted, two-sided Clopper–Pearson intervals with at least 95% joint coverage. Mapping through the plus-one formula and propagating lower and upper limits monotonically through BH yielded significant-count ranges of 36–37 for the uniform family and 8–11 for the matched family. These broad enclosures do not establish either outcome of the quarter criterion. The observed failure and its stability in the three redraws are therefore reported together with the remaining Monte Carlo uncertainty. The enclosures require independent identically distributed null draws within a cell; dependence between cells does not invalidate the Bonferroni union bound.

The analysis also changes eligibility: the matched coding comparison excludes sites with fewer than two consequence-compatible alternatives. Consequently, the difference between the two significant counts does not isolate a null-model change at fixed positions. The prescribed mutation weights are sensitivity assumptions and are not estimates of clinical ascertainment probabilities.

Sources and reproducibility: `independent_math_results.json` retains the five source rows; `historical_mc_stability.py` and `.json` produce the simultaneous enclosures; `historical_seed_redraw.py` and `.json` record the three new streams (2026102871, 2026102872, 2026102873). The seed redraws deliberately reuse the retained scientific producer and are not an independent implementation. No original manuscript, cache, or result file was edited.

# Complete companion to the genomic anchor audit

## Reader, purpose and exact basis

This is the complete research-and-teaching edition for Patrick Iben's *Auditing preprocessing-sensitive allele rankings in predicted chromatin contact maps*, the frozen author-review manuscript dated 28 October 2026, together with all six current additional files. It explains the main methods, mathematical statements, empirical results, all three main tables, all four main figures, limitations, reproducibility record, declarations and the supplements. The [concise study guide](STUDY_GUIDE.md) offers a shorter introduction; both editions have PDFs.

The intended reader has one statistics course. No genetics or persistence background is assumed. Read the ten guided lessons first, then use R01-R10 for detailed source reading, S01-S07 for the supplements, the six worked examples to check mechanisms, and the twelve practice questions to test interpretation. The glossary and researcher workflow support later use of the executable toolkit.

**Publication status:** this is an unsubmitted rework incorporating the earlier AlphaGenome audit. The earlier submissions were desk rejected for journal fit. Their archived preprint and reproduction deposit remain historical sources, not a new DOI or an active submission for this rework. The revised manuscript and study archive are publicly released; that release is not journal submission, journal acceptance or a new DOI.

**Exact-source contract:** [ARTIFACTS.json](ARTIFACTS.json) records the SHA-256 of the current main source and all six additional files. [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md) maps source spans and substantive objects to teaching units. Main-source hash: `05b28b1bcc1b3a715152beb5e07567afc628632851dba5d54e5301ea69483b5d`.

Completeness means an explicit teaching treatment of every substantive source component, including the supplement proofs, counterexamples and result-table interpretations. It does not mean copying each bibliography entry, reprinting all raw data, rerunning the research bundle inside the PDF, or claiming independent biological validation. Reported values are attributed to the frozen sources. Synthetic arithmetic illustrates a method and is not an additional genomic observation.

## How evidence is labeled

Definitions and mathematical proofs establish conditional statements. Model-output results describe delivered predictions. Statistical results depend on declared labels, nulls, sampling and multiplicity families. Exploratory checks remain exploratory. Prespecified spatial replication means its design preceded new spatial outcomes, not that the model's training set is known. Reproduction checks retained computations; it does not establish clinical truth.

Each detailed reading identifies its source and evidence type, explains the reasoning and supplies a question with an answer. Read the question before the answer. The twelve multiple-choice items are practice with feedback, not the original locked human transfer assessment. No human learner pass rate or educational efficacy is claimed. AI assisted adaptation, mathematical review and software verification; author scientific responsibility and human review remain distinct.

## Guided lessons: a first route through the manuscript

## P01. Start with the right object

A map, a diagram and a score answer different questions.

A contact map has a value for each pair of genomic bins. A persistence diagram summarizes when graph features appear and disappear as an edge threshold changes. A single aggregate score is a further summary; it cannot recover the map.

The study used predicted log-enrichment maps. These signed values are not observed read counts. The toolkit starts later in the workflow: you supply finite diagram coordinates and a declared shift. It does not request predictions or compute persistence from a contact matrix.

Keep reference and alternate bins, masks, track and filtration conventions aligned before creating diagrams. Changing that support changes the scientific comparison.

**Try it:** List which information a diagram preserves and which genomic locations it can discard.

**Boundary:** An abstract degree-one feature is not automatically a located chromatin loop.

Source: current manuscript lines 35–42; [source map](SOURCE_MAP.json).

## P02. A stable distance can still change a rank

Small score changes and large ranking changes can coexist.

Bottleneck distance matches diagram points while allowing points to be matched to the diagonal. The cost is the largest displacement in the best matching. A point can disappear at a cost equal to half its lifetime.

On the same finite support, a bound on every edge-value change bounds the resulting diagram distance. This is a standard stability result. It does not require treating an arbitrary contact transform as a metric.

Ranks answer a different question. If two scores are tied, even a small difference can select a unique leader. A stable numerical score therefore does not guarantee a stable rank.

**Try it:** Two scores are both 1.000. One becomes 1.001. Has the score changed much? Has the unique-leader decision changed?

**Boundary:** Mathematical stability does not establish biological calibration.

Source: current manuscript lines 35–42; [source map](SOURCE_MAP.json).

## P03. Move the origin, preserve interval lengths

Centering translates both coordinates of each interval.

For the study filtration, subtracting a map-wide mean adds that mean to every interval birth and death. The lifetime, death minus birth, stays fixed. The two maps can shift by different amounts.

Let delta be the alternate mean minus the reference mean. The audit computes the distance between the reference diagram and the alternate diagram shifted by lambda times delta. Lambda runs from zero to one. It is a preprocessing path, not a sequence or biological trajectory.

The distance can change by at most the absolute shift. Endpoint bounds enclose the intervening path. Exact equality at that bound forces a straight path; a small floating-point residual alone does not prove exact equality.

Two information settings matter. Whole-path envelopes use both native and centered endpoints after evaluation. The prospective endpoint audit instead uses native diagrams, native distances and the declared shifts before centered matching; those endpoint decisions do not automatically protect the whole path.

**Try it:** Use reference (0,4), alternate (1,5), and shift 0.25. Check that the lifetime stays 4 while distance rises from 1 to 1.25.

**Boundary:** Numerical near-saturation is not a formal certificate for unseen higher-precision model outputs.

Source: current manuscript lines 43–76; [source map](SOURCE_MAP.json).

## P04. Leave uncertain winners unresolved

A tolerance and score bounds make the ranking rule explicit.

The top set contains every score within the chosen tolerance of the maximum. When the selected allele belongs to a tie, fractional credit divides one by the size of that top set. Ties are not silently broken by array order.

Bounds can identify possible winners, guaranteed members of the top set, and guaranteed unique leaders. A sufficient native-margin bound can protect a strict leader throughout the path. When a bound is inconclusive, the right output is an unresolved set.

A Hausdorff witness is a lower bound obtained from nearest-point or diagonal distances. It can strengthen a decision without another full matching. It can miss multiplicity constraints, so it is not a replacement for bottleneck distance.

In a locked paired IMR-90 test, simple bounds identified 7 of 84 centered leaders and strengthened bounds identified 49: 42 additional decisions across six genes, with zero observed contradictions and 35 unresolved sites. The practical numerical allowance is not a full validated-arithmetic enclosure. Unresolved by the bounds does not necessarily mean that the directly computed centered scores are tied.

**Try it:** Increase the tie tolerance in the lab. Explain why a previously unique leader can become unresolved without changing any diagram.

**Boundary:** A unique maximum is not evidence that the selected allele is clinically correct.

Source: current manuscript lines 77–159; [source map](SOURCE_MAP.json).

## P05. Interpret the earlier AVI result precisely

A significant conditional result can have a negative observed margin.

The historical AVI counts rank Euclidean distances from a background centroid. They are not established rankings of raw AVI values. This distinction matters in a paper about anchor-sensitive rankings.

The mean statistic is the selected distance minus the larger competing distance. In the reported missense analysis the observed average was negative, but the simulated matched-null average was more negative. The significant result therefore describes enrichment relative to that null, not average superiority to the strongest alternative.

Some reported small adjusted values came from zero exceedances in a finite simulation. They are estimates at the simulation resolution floor. The frozen significant-count criterion and its remaining Monte Carlo uncertainty are both retained.

**Try it:** An observed margin is -0.01 and a simulated-null mean is -0.08. State one conclusion the difference supports and one it does not.

**Boundary:** Neither background-distance ranking nor null-relative enrichment supplies an independently validated pathogenic-versus-benign classifier.

Source: current manuscript lines 195–202; [source map](SOURCE_MAP.json).

## P06. Separate exact arithmetic from a scientific null

The calculation can be exact while the model remains conditional.

At each site, the study compared all three non-reference substitutions. Selected-allele credit records whether the clinically selected substitution is among the top scores, with ties sharing credit.

The label tests held the computed maps fixed and used specified probabilities for which allele would be selected. Exact finite-label arithmetic computes that conditional distribution without Monte Carlo sampling error. It does not make the selection process a randomized clinical experiment.

No discovery primary or sensitivity test survived Holm adjustment across the sixteen-test family. This did not establish the absence of every biological effect. Different representations and label models answer different questions.

**Try it:** Explain why exact probability arithmetic cannot prove that clinically selected alleles were exchangeable.

**Boundary:** Null reference intervals are not biological effect confidence intervals.

Source: current manuscript lines 117–128; [source map](SOURCE_MAP.json).

## P07. Find the mechanism before celebrating the ranking

Centering resolved many native ties without replacing strict leaders.

The discovery audit found numerical endpoint saturation across its computed allele comparisons. Some distances increased and others decreased. The sign of the response depended on relative diagram location.

Centering resolved 72 native ties while preserving all 45 strict native leaders. The observed path mechanism concerns how preprocessing changes the comparison. It does not by itself establish a useful gain in clinical discrimination.

Adding the absolute mean shift to the native distance reconstructed many centered top sets, but not all. Two diagrams can share the same native distance and shift while responding in opposite directions.

The earlier GM12878 saturation pattern did not universally transfer: 249 of 252 IMR-90 comparisons passed and three RB1 comparisons failed. Both simple and strengthened bounds already abstained at all three sites. The distinct witness gain is 42 decisions elsewhere, not unique detection of these exceptions. Exploratory direct samples showed two turning paths and one effectively flat path.

**Try it:** Compare alternates (1,5) and (-1,3) against reference (0,4), with the same positive shift. Why does the scalar native distance not tell you the direction?

**Boundary:** Local saturation is ordinary on a nonflat piece of a finite matching problem; its frequency is not a new generic theorem.

Source: current manuscript lines 160–194; [source map](SOURCE_MAP.json).

## P08. Ask what actually replicated

More unique ranks did not produce a consistent clinical-credit gain.

The new spatial cohort and protocol were fixed before those maps were acquired. It contained 84 sites in seven other loci. New spatial outcomes were prospective; independence from model training was not established.

All 66 native ties became unique maxima, and all 18 strict native leaders were preserved. Yet selected-allele credit fell descriptively from about 0.359 to 0.321. The sharper ranks and the selected-label outcome therefore moved in different directions.

The stronger witness bounds identified additional endpoint leaders beyond the simple margin check. This measures decision yield. A runtime speedup was not benchmarked, and no new confirmatory clinical-enrichment test was added.

IMR-90 reused the same 84 replication sites and the same AlphaGenome architecture. Its protocol preceded acquisition; native-only predictions were locked before centered distances were evaluated. GM12878 witness increments had been compared after those outcomes. A second output track adds neither independent loci nor an independent model.

IMR-90 selected credit rose descriptively from 0.335317 to 0.398810, whereas GM12878 replication credit fell. Native and centered RMS credits were 0.500000 and 0.517857 in IMR-90 and 0.444444 and 0.460317 in GM12878; all exceeded centered H1 in the corresponding track. More unique rankings did not establish clinical superiority.

**Try it:** Give a one-sentence conclusion that includes both tie resolution and the credit decrease.

**Boundary:** Eighty-four overlapping windows do not represent 84 independent genomic regions.

Source: current manuscript lines 98–173; [source map](SOURCE_MAP.json).

## P09. Match the conclusion to numerical resolution

Tolerance, delivered precision and solver error have distinct roles.

The delivered map values lie on a finite precision grid. This makes resolution relevant to ties, but does not isolate quantization as the cause of every tie or saturation event. Higher-precision source predictions would be needed for that comparison.

A tie tolerance defines an analysis convention. A numerical allowance is a claimed budget for computation error. Neither automatically becomes a physical detection limit. If coordinate units change, both must be scaled with the scores.

The paper reports numerical witnesses using practical allowances. It does not provide a complete interval-arithmetic certificate for every solver operation. The software likewise distinguishes numerical checks from formal real-arithmetic proof.

**Try it:** Multiply all diagram coordinates and shifts by ten. What else must be multiplied by ten to preserve the same ranking rule?

**Boundary:** Reproducing floating-point outputs does not reveal the model’s unexposed internal precision.

Source: current manuscript lines 129–136; [source map](SOURCE_MAP.json).

## P10. Use reproducibility to answer the right question

A rerun supports computation; independent measurements support biology.

The validation reran cached-input calculations and checked source-specific numerical claims. Replaying original random seeds can reproduce a simulation exactly without reducing its statistical uncertainty.

This toolkit adds synthetic examples and reusable software. Imported diagrams are processed locally in the browser. The study-summary panel reports aggregate author analyses, not raw contact maps.

The research contribution combines a specified preprocessing path, ranking bounds, useful witnesses, explicit unresolved cases and measured new-locus behavior. It is not a new generic distance, a physical loop detector or a clinical prediction tool.

The full v0.2.0 study archive is publicly released with the manuscript, code and verification records. Toolkit code is MIT-licensed; model outputs retain separate provider terms and attribution. Public release does not establish clinical validity, author journal approval or human learner transfer.

Declarations confirm no competing financial or nonfinancial interests and no specific grant or institutional funding. Codex assisted the work; Qwen3.8 earlier drafting; Qwen3.8-Max author-supplied QC checked against retained artifacts. AI checks are not external peer review; final author approval remains pending.

**Try it:** Describe one independent measurement that would be needed to connect the audit to a real structural chromosome change.

**Boundary:** The practice quiz has not been validated with human learners and does not replace author review.

Source: current manuscript lines 203–274; [source map](SOURCE_MAP.json).

## R01. Read the data object before selecting the method

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** definitions and interpretation.

A count matrix records sequenced contacts; a predicted log-enrichment matrix records model outputs relative to an expectation; an Atlas variant-by-track score summarizes a subset of prediction differences. These three objects are not interchangeable. The Atlas contact scorer is a local mean absolute reference-alternate prediction difference over interactions involving the variant-containing bin. The model's 2,048-bp spatial resolution does not turn a vector of track summaries into a spatial matrix.

If an idealized map is `L = log_b(C/E)`, exponentiation recovers the ratio C/E. Recovering C also requires E and the preprocessing conventions. Summing L, or summing its exponentiation, has not been established as absolute biological contact. Deterministic model inference removes fresh read sampling at that stage, but not model error; a model that enhances sampled Hi-C also inherits input uncertainty.

Three interventions need separate reasoning: thinning reads changes counts on existing bins; thinning vertices deletes bins; aggregation merges bins and sums contacts. The present genomic endpoint is an anchor change on fixed support. Neither depth robustness nor vertex-thinning behavior was empirically established by that endpoint.

**Check:** Would a scalar contact-track score let you locate a changed contact between two genomic bins? **Answer:** Not without the spatial information discarded during aggregation. The upstream object's information determines what topology can address.

## R02. What the filtration and its stability actually require

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** definitions and standard proof.

At threshold t, include all vertices, every edge with birth at most t, and every clique supported by those edges. The coefficient field is F2. Because the complete finite graph eventually becomes a simplex, its full degree-one filtration has no essential intervals. A threshold cutoff, missing support or censoring requires additional conventions.

No triangle inequality for edge births is needed. The transform `-log(C + epsilon)` need not be nonnegative or a metric. Calling it a weighted flag filtration avoids importing a false metric assumption. All reference and alternate comparisons must share bins, masks, track, diagonal exclusion and missing-data rules.

If corresponding edge births differ by at most epsilon, each complex is contained in the other after increasing the threshold by epsilon. This two-way inclusion bounds bottleneck distance by epsilon. It bounds the distance between diagrams, not the maximum vertical separation between Betti curves.

**Worked check:** For intervals (0,1) and (eta,1+eta), with eta between zero and one half, bottleneck distance is eta. Yet a threshold lying between the two births has Betti-one counts one and zero, so the supremum Betti-curve difference is one. Close diagrams can have visibly separated step functions.

## R03. Translation, invariant summaries and Figure 1

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** algebra and a synthetic illustration.

Native births are minus the predicted map. Subtracting an anchor from that map therefore adds the anchor to every birth and death. Common translation of both diagrams cancels in their distance; only the alternate-minus-reference anchor remains. The path parameter lambda is dimensionless; distances and shifts retain the diagram coordinate's units.

The operation preserves each lifetime, the count of full intervals, total persistence, maximum lifetime and the supremum of the full Betti-one curve. It shifts the thresholds at which those features occur. These invariances do not say that every reference-alternate comparison stays unchanged.

For m unordered edges, mean centering has supremum-norm operator constant `2 * (1 - 1/m)`. One coordinate can differ from the mean of the others, so removing a common level can amplify an entrywise perturbation. For positive weights, dividing by their sum before taking negative logarithms also adds a scalar origin shift. Neither identity establishes a biological calibration.

Figure 1 uses a synthetic four-bin cycle. Panel A shows intervals translated by global multipliers; B shows alignment after total normalization; C shows unchanged lifetime before normalization. It is an implementation illustration, not a genomic observation. Clipping, pseudocounts, finite windows and support changes do not inherit this identity automatically.

**Check:** If both diagrams receive the same scalar, what happens? **Answer:** Their mutual bottleneck distance is unchanged. If their scalars differ, lifetime invariance alone does not determine the distance response.

## R04. Endpoint geometry, witnesses and rank decisions

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** proofs and synthetic controls.

Let A and C be endpoint distances, T the absolute shift and lambda the path fraction. The lower envelope is the largest of zero, `A - lambda*T`, and `C - (1-lambda)*T`. The upper envelope is the smaller of `A + lambda*T` and `C + (1-lambda)*T`. These bounds use both endpoints. Exact endpoint change of magnitude T makes them coincide. A numerical residual near zero is a different statement.

For each point, take the smaller of its nearest opposite-diagram distance and its own diagonal distance, using the maximum-coordinate metric. The largest such value over both diagrams supplies the lower bound H. An increasing branch is determined when that lower bound meets `A + T`. A decreasing branch instead needs an upper witness, for example an explicit matching that costs `A - T`. An inconclusive lower witness cannot be promoted to a decreasing-branch certificate.

One subtle counterexample concerns edges that do not change native H1. A four-bin square has perimeter births zero and diagonal births one. Raising one diagonal birth to ten leaves the native interval (0,1) intact, but changes the six-edge mean by 1.5. Independently centered diagrams then have bottleneck distance 0.5. This proves a possible route by which an anchor changes a comparison; it does not identify the cause of any particular genomic tie.

A strict native leader i remains more than tolerance tau above j throughout the path if its native margin exceeds the sum of both absolute shifts plus tau. Numerical errors require additional margin. For valid score intervals [L,U], an allele is possible at the top when its upper bound reaches the largest competing lower bound minus tau. It is guaranteed in the top set when its lower bound reaches the largest competing upper bound minus tau. A guaranteed unique leader needs a strict gap above every competing upper bound plus tau.

The audit also records absolute mean change, native and centered RMS edge differences, maximum edge difference, interval-count changes and lifetime contrasts as transparent baselines. Clinical labels enter only the separately specified selected-allele summaries; they do not choose the anchor or lambda.

**Check:** Why keep an unresolved set? **Answer:** The available bounds may support several rankings. Imposing a total order would add a decision the evidence has not supplied. A possible set and a guaranteed set answer different questions.

## R05. Existing invariant distances and the novelty boundary

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** comparison with established work.

The shift-invariant bottleneck distance minimizes the distance over all diagonal translations. Sheehy, Kisielius and Cavanna already studied that problem. Dilation-invariant and normalized bottleneck work supplies other precedents. This paper audits a declared preprocessing path; it neither invents a generic metric nor chooses the shift that maximizes agreement with clinical labels.

On common edge support, half the range of the edgewise difference bounds the optimized shift-invariant diagram distance. It is an input upper bound, not the diagram-level optimum. Centering each map's own midrange differs from centering their difference. Full-cohort shift optimization was not performed.

Rank filtrations remove magnitude information under strictly increasing transformations, but can be sensitive to ties. Permuting genomic bin labels preserves an abstract persistence diagram. A method that summarizes abstract H1 can therefore miss which genomic location changed. Coordinate-sensitive baselines and located features such as boundaries, dots and flames are relevant when the intended endpoint is a physical structure.

**Check:** What is the proposed contribution? **Answer:** Combining a specified anchor path, bounds and witnesses, tolerance-aware partial rankings, numerical diagnostics and a new-locus replication to measure preprocessing consequences. The ingredients' established precedents remain part of that account.

## R06. Read the retained profile audit with its actual target

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** retained empirical results and stated design.

The initial coding cohort has 120 positions: DNM1 20, PCCA 15, PCCB 27 and MMUT 58. All three non-reference substitutions were scored. Most scorers used 400 background variants, with fewer for some. Dominant maximum-absolute pooling summarized profiles. Euclidean and Poincare comparisons jointly scaled each site's three profiles and centroid by their maximum norm; the Poincare transform used curvature -1 and radius fraction 0.8. Cosine comparison of scalar AVI was undefined and not interpreted.

The primary mean statistic subtracts the larger unselected distance from the selected distance, then averages. The declared family is 22 scorers times three geometries. The 384-position four-gene replication and 1,713-position seven-gene replication have different selection histories. The first sample came from capped recent ClinVar queries with an intronic-excluding parser; later pools used star-filtered records from a checksummed snapshot. They are selected study samples, not random variant populations.

Permutation analyses used 9,999 draws, plus-one p-values, BH within declared families and a BY check for the original primary family. Consequence matching restricts eligible pseudo-labels. The context model weights transitions by four and CpG transitions by a further ten before renormalizing. These are sensitivity assumptions, not measured ascertainment probabilities. The expanded-panel missense null retains its one uniquely missense-eligible position as a constant contribution; the coding consequence-matched analysis instead excludes positions with fewer than two eligible substitutions. Those eligibility rules are distinct.

| Retained reading | Reported result | What it means |
|---|---|---|
| Initial primary family | 17 of 66 BH-significant comparisons | A family-level result for the original profile endpoint. |
| Primary CONTACT_MAPS Poincare | Exact-tail bounds 0.014989-0.015035; BH q bounds 0.054961-0.055128 | Above 0.05; a later exploratory top-1 result does not replace it. |
| AVI nonsense/start loss | 1,095 of 1,238 first ranks, about 88% | Distances from the background centroid, not raw AVI ranks. |
| AVI missense | 94 of 246 first ranks, about 38% | A different consequence stratum, not a direct subtraction from a clinical benchmark. |
| Coding uniform versus matched null | 37 versus 10 significant comparisons | The frozen quarter criterion failed; eligibility changed from 1,490 to 452 AVI positions. |
| Missense outside chr13 | 58 of 170 first ranks, 0.341 | Retains the negative-margin versus null-relative distinction. |
| Other intronic splicing scorers | 46, 47 and 47 first ranks among 63 positions; q 0.000252 each | Conditional retained findings with Monte Carlo precision limits. |
| Canonical splice | No significant comparison among 63 scorer-by-geometry tests at 157 positions | A distinct stratum; cannot be pooled with the other-intronic result. |
| Exploratory consequence rule | Expected first choice 0.817 versus AVI 1,192/1,490 (0.800), including 3/6 synonymous positions | Post hoc, with random tie breaking for the rule; not independent validation. |

The retained missense observed mean was about -0.0128 versus simulated null mean -0.0829; outside chr13 these were -0.0407 and -0.0785. The significant q-values were 0.00132 and 0.00165. The negative observed margins preclude interpreting these as positive average leads over the strongest rival. AVI includes other predictors and consequence-related features; related computational evidence can also enter clinical labels. Post hoc, AlphaMissense alone also showed a missense preference, but it is an AVI input and therefore not an independent model baseline.

Changing the background centroid to a zero-effect origin retained sixteen significant Euclidean/Poincare comparisons in a separate 44-comparison sensitivity family. It does not imply identical p-values in all families. Historical top-1 used an argsort-selected maximum, while mean rank used midranks. Cache checks found no relevant ties in the highlighted AVI strata or the exploratory CONTACT_MAPS top-1 result, so those counts were unchanged. CONTACT_MAPS top-1 was 53/120 with exploratory q 0.0441, not the primary mean-statistic result above.

**Check:** Did switching to direct reference-alternate spatial distance repair every limitation? **Answer:** It removed the external background centroid by changing the endpoint. Consequence, pooling, ascertainment, label circularity and generalization still need separate evidence.

## R07. New spatial predictions and the conditional analysis

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** acquisition record, declared choices and conditional arithmetic.

The spatial analysis acquired real model-returned maps, rather than treating the cached track-score vectors as maps. For every original site, it obtained a primary reference and three alternate predictions on the prespecified GM12878 track, 4dn:4DNFIXP4QG5B / EFO:0002784. ALL_FOLDS evaluated a 1,048,576-bp interval, returning 512-by-512 maps with 130,816 unordered off-diagonal edges.

Coordinates and masks matched within sites, maps were finite and symmetric, and repeated reference predictions agreed. All 125,829,120 primary reference/alternate values were bfloat16-representable. This describes delivered values; it does not reveal the server's internal arithmetic. Every alternate differed from its reference. The median changed-edge count was 68,251, while the largest absolute mean signed change was about 0.00105435. Many altered predictions do not establish physical remodeling.

Native births used -L; centered intervals were translated algebraically; rank filtrations grouped equal values. Ripser used full H1 over F2. GUDHI exact-mode CGAL and Hera replaced an impractically slow initial solver without changing endpoints. Exact matching refers to supplied finite coordinates. Additional float32 conversion and induced-error bounds were tracked, without claiming a full real-arithmetic certificate.

The local protocol preceded spatial-outcome analysis but followed knowledge of the older profile audit. It is a local exploratory declaration, not public preregistration. The primary endpoint was centered fractional selected-allele credit with tolerance 0.000001. Native enrichment, rank enrichment and the paired centered-minus-native contrast completed four tests. Exact ties and tolerance 0.00001 were declared sensitivities.

Under independent uniform labels over three alternatives, expected fractional credit is one third even when ties occur. The paired test uses the same label under both representations. A sixth-credit lattice permits convolution of each site's finite distribution. Independent exact integer-polynomial/rational calculations reproduced all sixteen main and sensitivity tests. The largest discrepancy from reported floating values was 6.83e-16; an earlier exhaustive check differed by at most 3.22e-15.

Three sensitivity nulls applied consequence matching, mutation weights, and both. Matching retained all 120 sites, including 26 deterministic single-eligible-label contributions. These models condition on the computed outputs. Exact probability arithmetic does not establish independent biological regions or the truth of a clinical-label model.

**Check:** Why is one third still the uniform expectation when all three tie? **Answer:** Each possible label receives one-third credit, so averaging over the three equally likely labels still gives one third. A tie-aware score changes the distribution but preserves that expectation.

## R08. Read the discovery table, figures and mechanism

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** reported spatial results; post-label-analysis mechanism audit.

| Representation | Mean selected credit | Conditional p | Holm, four tests | BY, four tests |
|---|---:|---:|---:|---:|
| Native | 0.368056 | 0.124151 | 0.496606 | 0.73254 |
| Centered | 0.375000 | 0.175810 | 0.527429 | 0.73254 |
| Rank | 0.270833 | 0.937372 | 1 | 1 |
| Centered minus native | 0.006944 | 0.845665 | 1 | 1 |

The first three tests are one-sided enrichment above one third; the fourth is paired and two-sided around zero. No row passes the declared correction. The centered excess above one third is 0.041667, distinct from its native-to-centered change of 0.006944.

For centered sensitivity analyses, consequence matching had expected credit 0.3264, p 0.1001 and sixteen-test Holm 1. Mutation weighting gave 0.3187, p 0.06459 and Holm 0.896. Combining both gave 0.2953, p 0.006084 and Holm 0.09735. None passes the declared sixteen-test familywise threshold. Failure to reject is not proof that all biological effects vanish. The Holm correction is described in [Holm (1979)](https://www.jstor.org/stable/4615733); the main manuscript now cites it at first use.

Native, centered and rank representations had 75, three and one tied sites. Centering resolved 72 native ties and preserved all 45 strict leaders. Credit vectors changed at 73 sites, yet the average selected-credit gain stayed small. Conditional null reference intervals are not confidence intervals for biological effects. Resampling only four purposively selected genes cannot establish population-wide coverage.

Figure 4 shows the 120-site credits and descriptive gene-level points against the uniform one-third line. It does not select a favorable gene. Additional file 6 Figure S6.1 keeps input-order site zero. A is the reference map; B uses signed linear difference limits ±0.00390625, clipping 788/261632 off-diagonal cells (0.301%); C shows identical differences at the full ±0.01171875 range without clipping; D retains the three-allele distances. The contrast view improves visibility, not effect magnitude. Always compare its scale with the full-range control. These are predicted maps, not experimentally localized contact changes.

The later label-blind mechanism audit found all 360 endpoint changes near their translation bound, with maximum residual 2.08e-16 and no tiny shifts at 1e-10. Distances increased in 278 cases and decreased in 82. Endpoint-derived lines had no internal pairwise crossing; unique top sets rose from 45 at lambda zero to 111 at 0.1 and 117 at one. Every centered top set remained inside its native set.

The scalar native-plus-absolute-shift baseline reproduced 103 of 120 centered top sets; its failure elsewhere matters. A native-diagram Hausdorff witness met the increasing upper bound in 233 of 360 comparisons within 1e-12. These checks identify useful sufficient conditions, without making the mean shift a universal reconstruction or certifying exact real arithmetic.

**Check:** Why can there be no internal pairwise crossing while ranks become more decisive? **Answer:** A tie at the starting endpoint can split immediately, or cross a positive tolerance boundary, without two strictly ordered distance lines crossing in the open segment.

## R09. What was fixed before replication, and what replicated

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** prespecified new spatial outcomes and descriptive comparisons.

The cohort selected twelve sites in each of ASS1, BAP1, BRCA2, HFE, RB1, SCN5A and TSC1: 84 sites and 252 alternatives. A fixed SHA256 namespace selected sites within consequence strata, reserving one per nonempty stratum and allocating the rest proportionally. The gene-balanced design oversamples rare consequences relative to the eligible panel.

Reference bases were checked against GRCh38. Windows did not overlap discovery windows or windows in another selected gene, but overlapped substantially within genes. The cohort and protocol were hashed before new map acquisition. Historical nonspatial scorer outcomes already existed, so the prospective claim is specifically about new spatial outcomes and the method replication.

All planned sites completed without retries or missing data. Maps were finite and symmetric, returned reference repeats matched, and all 88,080,384 primary values were bfloat16-representable. The track, support and solver settings matched discovery; model-training independence and an immutable checkpoint were not established.

The protocol fixed numerical saturation within 1e-10 as the main descriptive endpoint, reported tiny shifts separately, retained the primary tie tolerance 1e-6 and specified exact/1e-5 sensitivities. Twenty-one direct midpoint checks used all three alternatives at one smallest-hash site per gene. No new confirmatory clinical-enrichment tests were added.

| Quantity | Discovery | Replication |
|---|---:|---:|
| Sites / loci | 120 / 4 | 84 / 7 |
| Reference-alternate comparisons | 360 | 252 |
| Numerically saturated | 360 / 360 | 252 / 252 |
| Native tied top sets | 75 | 66 |
| Native ties resolved | 72 | 66 |
| Centered tied top sets | 3 | 0 |
| Strict native leaders replaced | 0 | 0 |
| Native leaders passing whole-path margin | 45 | 18 |
| Unique centered leaders from native-diagram bounds | 89 / 120 | 52 / 84 |
| Native-plus-absolute-shift top-set agreement | 103 / 120 | 64 / 84 |
| Native selected credit | 0.368056 | 0.359127 |
| Centered selected credit | 0.375000 | 0.321429 |

All replication shifts were non-tiny and numerically saturated; maximum residual was 2.22e-16. Distances increased 182 times and decreased 70 times. The midpoint calculations agreed with endpoint lines to at most 8.33e-17. Turning, flat, affine, zero-shift and multiplicity controls tested behavior beyond the increasing saturated case.

All 66 native ties became unique and all eighteen strict leaders remained. Every centered top set was inside its native set; no new ties or internal pairwise crossings appeared. Unique top sets at lambda 0.01, 0.1, 0.25 and 0.5 numbered 29, 73, 76 and 84. All genes and leave-one-gene-out summaries were retained.

Witness-strengthened endpoint bounds identified 89 discovery and 52 replication leaders, leaving 31 and 32 unresolved. A post-result comparison counted 44 and 34 additional resolutions beyond the simple margins, without losing their 45 and eighteen resolutions. These endpoint decisions did not use centered distances or labels for selection. Whole-path protection belongs to the separate native-margin condition. No runtime speedup was benchmarked. The increasing witness met its upper bound in 145 of 252 replication comparisons.

At tolerance 1e-5, eleven replication sites remained tied after centering, versus none at 1e-6; native ties remained 66. The selected-credit change was -0.037698. Native and centered RMS map-difference credits were 0.444444 and 0.460317. The scalar baseline had the same aggregate credit as centering but agreed on only 64 of 84 top sets. Matching one average does not mean matching decisions.

Figure 3's panels separate distance changes and translation bounds (A), unique top sets along lambda (B), selected credit (C), and preserved leaders/ties resolved (D). Step curves come from tolerance breakpoints in an endpoint-derived affine approximation; fixed-grid points and independent midpoint checks have separate roles. The figure contains no model-accuracy or independent-biological-sampling uncertainty band. Lambda was not optimized using selected labels.

**Check:** Which headline replicated? **Answer:** The preprocessing mechanism: numerical saturation, tie resolution and preservation of strict leaders. A consistent improvement in clinically selected-allele credit did not replicate.

### Paired IMR-90 validation: coverage transfers, universal saturation does not

Additional file 4 describes a second AlphaGenome output track at the same 84 sites, not a second architecture or independent locus set. Both tracks were requested in the same 252 calls; contemporary GM12878 maps exactly matched historical outputs at these inputs. This checks observed drift, not immutable weights. All native diagrams, shifts, bounds and predictions were locked before IMR-90 centered evaluation.

| Paired IMR-90 outcome | Value |
|---|---:|
| Simple / strengthened leaders | 7 / 49 of 84 |
| Additional decisions / genes with gains | 42 / 6 |
| Unresolved after strengthening | 35 |
| Contradicted leaders | 0 |
| Saturation passes / comparisons | 249 / 252 |
| Native ties resolved / native ties | 74 / 75 |
| Strict native leaders preserved | 9 / 9 |
| Native / centered selected credit | 0.335317 / 0.398810 |
| Native / centered RMS credit | 0.500000 / 0.517857 |

The utility benchmark required 17 additional leaders across at least four genes. It was selected before acquisition, not a powered clinical threshold. The observed gain was ASS1 7, BAP1 11, BRCA2 7, HFE 4, RB1 0, SCN5A 6 and TSC1 7. Removing any one gene left 31–42 additional decisions. The gain was 43 at zero tolerance and 35 at 1e-5. No lost simple decisions is structural because strengthening cannot lower the lower bound; the measured contribution is the amount of additional usable coverage.

All three saturation failures occurred in RB1. Both simple and strengthened bounds had already abstained at their three sites. The witness-specific gain was elsewhere. Seven-point exploratory queries, specified after the primary result, found two sampled paths changing direction and one flat within 1e-12. All samples lay inside the endpoint envelopes. A flat path is affine but not unit-speed saturated; nonsaturation alone does not prove nonlinearity. Sampled turning behavior does not reveal an exact breakpoint or matching identity.

The 21 prespecified midpoint checks all passed their chord and envelope tolerances; one happened to sample the flat exception. Those checks did not rule out turning in the other exceptions. The later diagnostics did not change the primary criteria. Figure 2 separates native-only coverage, descriptive selected credit and ranking decisiveness. Additional file 4 shows all exception paths, not a favorable subset.

IMR-90 credit improved descriptively while GM12878 replication credit declined. RMS baselines exceeded centered H1 in both tracks; IMR-90 absolute mean-change credit (0.410714) was also higher. Native top sets agreed between tracks at 33/84 sites, centered sets at 35/84. Aggregate agreement is not identical allele decisions. There is no clinical accuracy claim, runtime benchmark, independent-model transfer or validated arithmetic enclosure.

**Transfer check:** What survived the failed saturation generalization? **Answer:** The bounded audit's additional numerical decision coverage on this paired track. Universal saturation failed, and both methods abstained at the exceptions. The audit never required every path to be saturated.

## R10. Reproducibility, limitations and declarations

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** interpretation, retained validation record and author declarations.

The maps are predictions for GM12878 and IMR-90 tracks within one AlphaGenome model; the paired track test reuses the same 84 replication sites. The selected ClinVar sites were not chosen for experimentally verified contact disruption. Selected versus unselected substitutions are not an independently established pathogenic-versus-benign benchmark. The eleven loci, within-gene window overlap and consequence-stratified sampling limit generalization. Historical scorer exposure, possible training overlap and the ALL_FOLDS alias limit stronger holdout or checkpoint claims.

The bfloat16-representable values make numerical resolution relevant. They do not prove that quantization caused every tie or every saturated segment. A higher-precision comparison is needed for that causal attribution. PH input-conversion bounds and solver allowances have different scope from a complete validated-arithmetic certificate. Abstract H1 also discards genomic labels; experimental maps, known local perturbations and coordinate-sensitive comparisons remain open validation tasks.

The frozen main manuscript reports a later fresh-environment regeneration of all 204 spatial sites from cached maps. All 6,324 checked per-site comparisons met their tolerances; eighteen centered-distance vectors differed only at floating rounding scale. Six retained historical outputs regenerated byte-for-byte with original seeds. All sixteen conditional tests were separately recertified. These are reported research-bundle checks, not a new execution of that entire bundle by this teaching PDF. Reproducing a fixed simulation seed does not measure Monte Carlo precision or model accuracy.

The research record includes per-call maps, diagrams, track metadata, coordinates, protocols, failure records and source hashes. The versioned public release distributes reusable code and teaching materials together with a separate full study archive carrying provider output notices. The old reproduction deposit and old preprint are historical sources, not deposits or DOIs for the revised manuscript. Public code release does not imply journal submission or publication of the rework.

The confirmed declarations report public annotations and computational outputs, no specific grant or institutional funding, and no competing financial or nonfinancial interests. OpenAI Codex assisted development, derivations, code, validation, prose and source checks; Qwen3.8 assisted earlier drafting and Qwen3.8-Max generated author-supplied QC reports checked against retained artifacts. These checks are not external peer review. AlphaGenome produced molecular predictions. The author retains responsibility; final author approval and human learner effectiveness remain uncertified.

The current main bibliography groups model/output context, topology and invariant-distance precedents, clinical annotations and computational-evidence guidance, inference methods, the earlier archive, and toolkit sources. The additional files use local bibliography numbering. Citing these sources does not independently reproduce their findings.

**Check:** What would turn this into evidence about physical chromatin architecture? **Answer:** A validation design with relevant experimental structural measurements or perturbations, appropriate location-sensitive comparisons and justified sampling. Agreement among model-output computations is not that experiment.

The full study archive is released with [v0.2.0](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0), alongside the public manuscript, code, protocols and verification records. Toolkit code is MIT-licensed; provider model outputs retain their separate terms and attribution notices. Public availability supports reproduction, not clinical validity, author journal approval or human learner effectiveness. Additional file 6 separates stored-input replay and 252 independent witness checks from model validity and notes that replay shares the PH kernel.

## S01. Vertex thinning: when extinction is a finite-set statement

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** finite-set proof, counterexamples and a conditional sampling identity.

Retain each of N fixed bins independently with probability p. A flag complex with at most three vertices has no degree-one homology: a three-cycle is filled by its triangle. Any statistic that is zero for an empty degree-one diagram can be nonzero only if at least four bins survive. The statistic or filtration transformation may depend on p or the retained count, provided it preserves that zero. For every positive epsilon:

`P(|T_p| > epsilon) <= P(Binomial(N,p) >= 4) <= choose(N,4) * p^4`

The last inequality counts retained four-subsets. It is a probability bound for fixed N, not a universal fourth-power law for persistence amplitude or the expectation of an arbitrarily rescaled statistic. It only needs empty degree-one diagrams on at most three vertices; it does not assert that every such complex is contractible.

Deleting vertices can increase persistence at intermediate p. Removing a hub can expose the four-cycle it previously filled. If N grows, p tending to zero alone is insufficient; Np tending to zero suffices. Four growing groups arranged around a cycle can retain a feature if each group continues to have surviving vertices. Neither statement is a theorem about ordinary sequencing-depth reduction on fixed bins.

If at least m bins survive, choosing a uniform m-subset of the survivors is, after averaging over independent equal-p retention and conditioning on eligibility, uniform among original m-subsets. Symmetry gives this conditional comparison. It neither restores the full-map target nor removes declining eligibility.

For a fixed map, let a_j count j-bin subsets with positive-length H1. The exact nonempty-diagram probability is the sum, over j from four to N, of `a_j * p^j * (1-p)^(N-j)`. If k is the smallest j with a positive count, the leading order is `a_k * p^k`. Extra vertices can fill a witness, so nonemptiness need not be monotone in retained sets.

**Worked check:** A four-cycle with later diagonals survives only when its four bins survive, giving p^4. A chord-completed five-cycle with perimeter births zero and chord births one has nonempty H1 only when all five survive, giving p^5. At p = 0.5 these probabilities are 1/16 and 1/32. These are synthetic finite examples, not measured genomic thinning curves. A particular statistic can still vanish on a nonempty diagram.

## S02. The exact endpoint proof and its numerical counterpart

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** proof and numerical interpretation.

Matching each interval to its translated copy bounds the distance between two translated diagrams by the absolute difference of their shifts. The metric triangle inequality then gives a one-Lipschitz function of translation. To treat either sign of delta, let T be its absolute value and let u run from zero to T in the chosen direction.

The lower endpoint cone is the maximum of zero, `A-u` and `C-(T-u)`; the upper is the minimum of `A+u` and `C+(T-u)`. For direction r equal to plus or minus one, define deficit `kappa = T - r*(C-A)`. It is nonnegative and gives:

`u - kappa <= r*(g(u)-A) <= u`

If the endpoint change equals T in magnitude, choose r in its direction and the deficit is zero: the path must be affine throughout the segment. The proof does not require a fixed optimal matching and says nothing about extending the line beyond the segment.

With endpoint estimates and proved errors e0 and eT, replace the deficit by the upper bound `K = T - r*(C_hat-A_hat) + e0 + eT`. The whole path lies within `e0 + K` of the corresponding line. For nonsaturation use the general endpoint envelopes with errors subtracted below and added above. At zero shift the path is constant and saturation is trivial.

The word proved matters. A complete budget must cover input conversion, recovered coordinates, translation, mean estimation when the target is an exact-real mean, distance evaluation and returned rounding. Solver exact mode and the filtration's float32 audit alone do not establish that budget. If delta is uncertain, either explicitly target the stored shift or add its uncertainty using the same Lipschitz bound.

**Worked check:** Take A = 1, T = 0.25 and C = 1.25. At halfway the two exact cones meet at 1.125. If the same endpoints are only known within an error, the cones form a nonzero tube. The number 1.125 is then a reference line, not automatically a certified exact value.

## S03. Three local slopes and a prospective matching certificate

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** finite matching derivation and sufficient local condition.

For one real-real point pair, average the birth and death differences to obtain c, and take half the absolute difference of those two differences to obtain q. Its L-infinity cost after translation t is exactly `|t-c| + q`. A diagonal cost is constant at half the lifetime. For one partial matching, the largest cost is the maximum of a line of slope -1, a line of slope +1 and a constant. Minimizing over finitely many matchings yields a continuous piecewise-affine distance with local slopes -1, zero or +1. The lower envelope need not be convex: identical interval (0,2) gives `min(|t|,1)`. These slopes are measured against the shift t. Against the normalized path fraction lambda, the possible slopes are -T, zero and +T, where T is the absolute relative shift.

For a native distance b greater than zero, form the augmented finite bipartite graph. Its left side contains real D points and diagonal copies of E; its right side contains real E points and diagonal copies of D. Include all real-real edges, each real point's own diagonal edge, and all dummy-to-dummy edges at cost zero. A perfect matching then represents a persistence matching. Classify edges by native cost: below b, equal to b, or above b. The critical real-real edges have directional slope -1 when the chosen direction points toward their corner c, and +1 otherwise; diagonal edges have slope zero.

Let gamma be the smallest nonzero difference between an edge cost and b. A sufficient radius R is the smaller of gamma/2 and the positive corner distances of decreasing critical real-real edges. An absent corner minimum is infinite; dummy zero-cost edges ensure a gap exists when b is positive. Before R, noncritical edges cannot cross the candidate levels, and the critical slopes stay fixed.

Build three threshold graphs, adding all low edges and critical edges with slope at most -1, then zero, then +1. The smallest threshold slope admitting a perfect matching is the exact one-sided slope for `0 <= u < R`. A native-optimal matching must use a critical edge; otherwise b was not minimal. That fact makes the threshold argument decisive without seeing the centered endpoint or clinical label.

The radius is conservative and can be much shorter than the actual anchor shift. A certificate at the origin cannot be extrapolated past R. Native distance zero needs separate degeneracy treatment. If every stored coordinate lies on a common affine lattice with spacing g, candidate costs occur on half-lattice steps and the conservative radius is at least g/4. Source quantization alone does not prove the recovered diagram coordinates share that lattice.

**Check:** Does seeing slopes -1, zero and +1 make the genomic saturation frequency unexpected? **Answer:** No. Small shifts inside nonflat pieces necessarily saturate. The empirical contribution is which pieces the chosen preprocessing traverses and what that does to allele decisions.

## S04. Increasing and decreasing witnesses, including empty diagrams

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** bounds and counterexample.

For each point in either diagram, find the cheaper of its closest opposite real point and its diagonal. Take the largest of these costs over both directions. Distance to an empty real set is infinity, so an empty opposite diagram correctly leaves the diagonal option. Every complete matching must pay at least this bound H.

For increasing saturation, `H(delta) <= C <= A+T`. If the endpoints of this inequality meet, no extra shifted matching is needed to establish that endpoint. With an upper enclosure A_up and lower witness H_low, the increasing deficit is at most `A_up + T - H_low`.

For decreasing saturation, use an explicit shifted matching upper bound U and the universal lower bound `A-T`. The decreasing deficit is bounded by `T + U - A_low`. A nearest-neighbor lower bound alone does not supply U.

Multiplicity is the obstruction to replacing matching with H. Two identical intervals can share the same nearest real point, while a valid matching cannot reuse it. The worked multiplicity example later gives H zero but bottleneck distance two.

**Check:** Is the witness independent evidence of biology? **Answer:** No. It is independent of the centered complete-matching calculation, conditional on the native diagrams and chosen anchor. It is another mathematical route to the same specified comparison.

## S05. Tolerance boundaries and reliable partial rankings

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** standard margin arguments.

For exactly saturated paths, each score is a line with native intercept and signed shift slope. Pairwise equality occurs where the intercept difference plus lambda times the slope difference is zero. For an inclusive tolerance-defined top set, also include where that difference equals plus or minus tau. Parallel and identical lines require separate handling. The roots partition the path into intervals with fixed membership, with the inclusive boundary convention checked explicitly.

An exact tie at lambda zero can split for every positive lambda when tolerance is zero. At positive tolerance, a pair separates only when lambda times the absolute slope difference exceeds tau. A discontinuous decision rule can coexist with a stable distance.

For Cartesian score intervals, possible and guaranteed memberships use competing lower and upper bounds respectively. Their formulas are exact for independently admissible intervals; dependent errors can make them conservative. Whole-path decisions can use envelope extrema. A slope-aware certificate minimizes the pairwise affine margin at the interval endpoints, subtracts both tube errors and compares with tau. This can improve on the simpler absolute-shift margin, when its assumptions are justified.

**Worked check:** If A lies in [1.2,1.3] and B in [0.6,0.8], tolerance 0.1 leaves A more than 0.1 above B for every allowed pair. If A's lower bound falls to 0.8, that claim is no longer guaranteed. The upper endpoint 1.3 does not rescue a worst-case statement.

The design must fix tolerance, error budget, analysis targets and baselines before looking at new outcomes. Choosing lambda to favor selected labels and then calling the result predeclared changes the inferential question.

## S06. Rank filtrations, prior art and finite checks

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** perturbation argument, counterexample, prior-art boundary and reported verification.

Group equal edge values and replace each by the fraction of eligible edges preceding it. A strictly increasing transform preserves this rank filtration. Entrywise stability of a weighted filtration does not automatically carry over: if raw perturbations are at most delta, only pairs whose original gap is at most twice delta can change order. With m eligible edges, the bound is `max_e count{f != e: |w_f-w_e| <= 2*delta} / m`: for each edge, exclude itself, count potentially reordered neighbors, then take the largest count and divide by m.

At exact ties, no uniform continuity bound tending to zero with delta can hold. In an all-tied four-bin graph, making the perimeter slightly earlier than both diagonals creates a rank interval of length two thirds, however small the raw split. Rank removes magnitude information more broadly than centering, and may magnify tie decisions. None of the abstract diagrams records genomic bin identity.

The closest identified invariant-distance precedents are Sheehy, Kisielius and Cavanna (2018), Cao and colleagues (2023), and May, Krishnamoorthy and Gambill (2024). The supplement does not claim an exhaustive review of all parametric matching or robust-ranking work, nor priority for endpoint rigidity, finite-cell slopes or interval margins.

The recorded Fraction-based verifier enumerated 250 small rational diagram pairs, passed 498 directional local-slope cases with 1,494 exact evaluations, and passed 4,500 endpoint-cone/deficit-tube checks. It included affine, turning, capped, opposite-slope and multiplicity examples. These are finite implementation checks; universal statements rest on their proofs. They are not a proof-assistant formalization or certification of the full genomic calculations.

**Check:** Which operation is appropriate if physical loop location is the target? **Answer:** An abstract diagram alone is insufficient; retain or separately compare coordinates and the located feature. Transformation invariance has an information cost as well as a benefit.

## S07. Monte Carlo precision is not biological uncertainty

**Source:** current manuscript/additional-file spans mapped by this unit in [COMPLETE_COVERAGE.md](COMPLETE_COVERAGE.md). **Evidence:** retained simulation estimates and post-result precision checks.

The five highlighted profile cells each had zero exceedances in 9,999 null draws. Their plus-one raw p-value is `(0+1)/(9999+1) = 0.0001`. The recorded plug-in MCSE is 0.0001, a diagnostic estimate rather than a known true standard error at the boundary. The recorded Wilson interval for the exceedance probability, mapped through the plus-one formula, was [0.000100,0.000484]. This is conditional simulation precision, not uncertainty about biological effects.

| Profile comparison | Sites | Exceedances / draws | Raw p | BH q |
|---|---:|---:|---:|---:|
| AVI, matched/context-weighted missense | 246 | 0 / 9,999 | 0.0001 | 0.00132 |
| Same, excluding chr13 genes | 170 | 0 / 9,999 | 0.0001 | 0.00165 |
| Other intronic: splice junctions | 63 | 0 / 9,999 | 0.0001 | 0.000252 |
| Other intronic: splice sites | 63 | 0 / 9,999 | 0.0001 | 0.000252 |
| Other intronic: splice-site usage | 63 | 0 / 9,999 | 0.0001 | 0.000252 |

The observed AVI margins are negative even when the null-relative difference is positive:

| Missense comparison | Observed mean | Simulated null mean | Difference |
|---|---:|---:|---:|
| All 246 positions | -0.012798807 | -0.082914582 | 0.070115775 |
| 170 outside chr13 | -0.040677371 | -0.078455404 | 0.037778033 |

The null means average 9,999 draws and are not exact expectations. The q-values are jointly adjusted point estimates in specified families; a raw-p MCSE cannot be relabeled a q-value standard error. The exploratory CONTACT_MAPS top-1 q-value 0.0441 came from a binomial test, not these Monte Carlo mean-statistic cells.

The frozen significant counts 37 and ten fail the planned quarter criterion because ten exceeds 9.25. Three new independent random-number streams, still using 9,999 draws and the same producer, reproduced those two counts. They test seed sensitivity; they neither replace the original criterion nor provide an independent implementation.

A separate simultaneous precision check used Bonferroni-adjusted two-sided Clopper-Pearson intervals across 132 probabilities with at least 95% joint coverage, then propagated plus-one and BH bounds monotonically. The resulting possible significant-count ranges were 36-37 uniform and 8-11 matched. These ranges do not establish either outcome of the quarter criterion. They require independent identically distributed draws within each cell; dependence across cells does not defeat the Bonferroni union bound.

Eligibility also changed because matched coding analyses omitted sites with fewer than two eligible substitutions. Differences in counts therefore mix a changed null with a changed position set. Analyst-chosen mutation weights are not clinical ascertainment estimates. The spatial finite-label tests have no Monte Carlo sampling error, but retain their own scientific-null assumptions.

**Check:** Can three agreeing redraws certify the exact q-values or the quarter decision for every possible simulation run? **Answer:** No. They provide observed seed stability. The simultaneous intervals retain uncertainty that the three redraws alone do not eliminate.


## Worked examples: six synthetic checks

Every example here is synthetic. Coordinates describe finite persistence intervals, not genomic positions or experimentally measured contacts. They can be checked by hand. The browser evaluates the sampled path directly; the endpoint lines are not assumed to be correct for every example.

### W01. Break a native tie without changing any lifetime

Use a reference diagram `D = {(0, 4)}` and three alternates:

| Alternate | Native diagram | Declared shift delta | Native distance |
|---|---|---:|---:|
| A | {(1, 5)} | 0.25 | 1 |
| B | {(-1, 3)} | 0.25 | 1 |
| C | {(0.5, 4.5)} | 0.25 | 0.5 |

Every interval has lifetime 4. Shifting both coordinates preserves that lifetime.

At centering fraction lambda, the three distances on this segment are:

- A: `1 + 0.25 lambda`
- B: `1 - 0.25 lambda`
- C: `0.5 + 0.25 lambda`

The real-point matching is cheaper than sending the points to the diagonal throughout this segment. At lambda = 1, the distances are 1.25, 0.75 and 0.75. The native top set `{A, B}` becomes the unique leader `{A}`.

If B is the selected label, its top credit falls from 1/2 to zero. That label is an illustrative choice; it does not make B clinically correct. The example shows that a more decisive ranking need not improve selected-label credit.

With tie tolerance 0.1, A and B remain in the same top set through lambda = 0.2, including the boundary in exact arithmetic. They separate only when `0.5 lambda > 0.1`. Numerical implementations also have finite-precision limits near a boundary.

**Try it:** keep the diagrams fixed and change the tolerance. Which changes come from the distance, and which come from the rank rule?

### W02. The same scalar information can have opposite effects

Against `D = {(0,4)}`, compare `E+ = {(1,5)}` and `E- = {(-1,3)}`. Both start at distance 1. Both receive the same shift 0.25.

The first distance becomes 1.25; the second becomes 0.75. Thus the native distance and scalar shift alone cannot universally reconstruct the centered distance. Relative diagram location supplies directional information that those two numbers omit.

**Try it:** explain why “the mean shift determines the response” is stronger than the evidence permits.

### W03. Endpoints alone need not trace a straight line

Use `D = {(0,4)}`, `E = {(-1,3)}` and delta = 2. The distance along the segment is `|2 lambda - 1|`.

It starts at 1, reaches zero at lambda = 1/2, then returns to 1. Its endpoint change is zero although the allowed shift magnitude is 2. The endpoint envelopes contain the path, but a straight interpolation between the endpoints would miss the turn.

The exact-saturation theorem is conditional: only when the absolute endpoint difference equals the shift bound do the envelopes collapse to a line. A useful audit must include nonsaturating controls such as this one.

### W04. Diagonal matching creates a flat cap

Use `D = E = {(0,2)}` and delta = 2. Direct point-to-point matching costs `2 lambda`. Matching each interval to the diagonal costs 1. Therefore the bottleneck distance is `min(2 lambda, 1)`.

The path rises and then becomes flat. This is another reason not to infer a straight full path merely because some short segment looks linear.

### W05. A nearest-neighbor bound can miss multiplicity

Let `D` contain **two copies** of `(0,4)` and `E` contain one copy. Every real point has an identical nearest point in the other diagram, so the diagonal-augmented Hausdorff bound is zero.

A matching cannot use the single E point twice. One D point must go to the diagonal at cost 2. The bottleneck distance is therefore 2. Keep repeated points in imported data; deduplication changes the object.

### W06. Strong versus inconclusive ranking bounds

Suppose an audit supplies valid centered-score intervals A: `[1.2,1.3]`, B: `[0.6,0.8]`, C: `[0.7,0.9]`, with tolerance 0.1. A is always more than 0.1 above the other scores, so A is a bound-supported unique leader.

If A instead has interval `[0.8,1.3]`, the same conclusion is no longer secured. An unresolved result is useful: it identifies where another matching calculation or a tighter error bound could change the decision.

These are statements conditional on the validity of the input bounds. A practical floating-point allowance is not automatically a proof that every numerical operation is enclosed.

### Worked-example source and scope

The translation, endpoint, opposite-slope, multiplicity and ranking arguments correspond to the anchor-path, endpoint-envelope and native-only prediction sections of the current manuscript identified in [SOURCE_MAP.json](SOURCE_MAP.json). The three-alternate tie example and interval-ranking exercise are teaching constructions. They are not additional genomic findings or a claim of new generic persistence theory.


## Glossary

- **Anchor:** The map-wide scalar used to set the origin of the diagram coordinates.
- **Alternate allele:** A non-reference DNA base at the same genomic position.
- **Bottleneck distance:** The smallest possible largest matching cost between two diagrams, allowing diagonal matches.
- **Birth and death:** Thresholds at which a persistent feature appears and disappears.
- **Centering:** Subtracting a declared map-wide mean from a map.
- **Conditional null:** A specified model for labels while the observed maps and analysis choices are held fixed.
- **Diagonal match:** Matching an interval to birth = death at a cost of half its lifetime.
- **Fractional top credit:** Credit of one divided by the tied top-set size when the selected allele belongs to that set; otherwise zero.
- **Hausdorff witness:** A nearest-point-or-diagonal lower bound on the bottleneck distance; it does not enforce matching multiplicities.
- **Lifetime:** Death minus birth for one persistence interval.
- **Monte Carlo error:** Uncertainty introduced by estimating a probability or expectation using a finite number of random draws.
- **Persistence diagram:** A collection, with multiplicity, of feature birth/death coordinate pairs.
- **Saturation:** An endpoint change that attains its mathematical Lipschitz bound exactly; numerical near-saturation is a separate empirical statement.
- **Selected allele:** The clinically selected allele in the research design, not an independently proven correct prediction for each test.
- **Tie tolerance:** The score gap that the analysis treats as unresolved.
- **Unresolved set:** Alternatives whose supplied score bounds do not yet justify a single winner.

### Keep these distinctions

- Synthetic presets are teaching examples, not genomic observations.
- The toolkit does not infer pathogenicity or locate chromatin loops.
- Numerical near-saturation is not formal real-arithmetic certification.
- Aggregate results concern two output tracks of one model; the paired test reuses the same 84 sites and overlapping loci.
- The interactive quiz is practice with answer feedback, not a validated human transfer assessment.


## Practice questions and explained answers

These multiple-choice practice items adapt the source reading guide. They are not the locked free-response human transfer test used in the manuscript validation harness. No learner pass rate or educational effectiveness is claimed.

Try each question before reading its answer. Correct feedback explains the distinction; a score is not evidence of educational effectiveness. Retrying is encouraged.

### T01 · Core

What input does this toolkit directly audit?

1. Finite persistence diagrams plus a declared shift
2. Raw sequencing reads
3. A list of pathogenicity labels

**Answer: 1.** The toolkit starts from diagram coordinates. Map acquisition and persistent-homology construction are upstream steps.

### T02 · Core

What stays unchanged when both coordinates of each interval receive the same shift?

1. Every distance between two independently shifted diagrams
2. Each interval’s lifetime
3. Every allele ranking

**Answer: 2.** Death minus birth is unchanged. Different shifts of the two diagrams can still change their distance and the resulting ranks.

### T03 · Core

For a valid 1-Lipschitz anchor path, what does exact endpoint saturation imply?

1. The selected allele is pathogenic
2. The same matching remains optimal everywhere
3. The path is affine on that segment

**Answer: 3.** The endpoint envelopes coincide. This conclusion does not require a fixed matching or extend beyond the segment.

### T04 · Core

Which statement describes the GM12878 new-locus replication?

1. More ties resolved, while selected-allele credit decreased descriptively
2. Every clinical metric improved
3. An experimental loop perturbation was validated

**Answer: 1.** Tie resolution and selected-label credit are different outcomes. More unique ranks did not establish improved clinical discrimination.

### T05 · Boundary

A floating-point saturation residual is very small. What has been established?

1. Exact equality for unseen real-valued model outputs
2. Numerical near-saturation on the computed inputs
3. The biological model has no error

**Answer: 2.** A tiny computed residual is numerical evidence. A formal enclosure needs justified error bounds for every relevant operation.

### T06 · Boundary

What does an exact conditional label test guarantee?

1. The clinically selected labels are exchangeable
2. Overlapping windows are biologically independent
3. The specified finite-label probabilities were computed without simulation error

**Answer: 3.** Exact arithmetic addresses the calculation, not the truth of the label model or biological independence.

### T07 · Boundary

A mean margin is negative but exceeds its conditional-null mean. A significant test supports which reading?

1. Enrichment relative to that null
2. A positive average lead over the strongest alternative
3. Validated clinical accuracy

**Answer: 1.** A statistic can be negative yet unusually large under a more-negative null. The observed and null-relative effects must both be reported.

### T08 · Boundary

Does this model-output audit establish physical chromatin remodeling?

1. Yes, whenever the diagram distance changes
2. No, independent structural evidence is still needed
3. Yes, if all ties disappear

**Answer: 2.** Predicted maps and abstract intervals are not direct experimental evidence of a located chromosome change.

### T09 · Transfer

All coordinates and shifts are multiplied by ten. How should a fixed-unit ranking rule be transported?

1. Keep the tolerance unchanged
2. Divide the tolerance by ten
3. Multiply the tolerance and numerical allowance by ten

**Answer: 3.** Distances scale with the coordinate unit. Co-scaling thresholds preserves the intended comparisons.

### T10 · Transfer

A finite simulation produces zero exceedances. What should be reported?

1. The plus-one estimate, draw count and Monte Carlo uncertainty
2. A true tail probability of exactly zero
3. An adjusted-value standard error obtained by rescaling a raw-p error

**Answer: 1.** Finite simulation has a resolution floor. Raw-p uncertainty cannot simply be relabeled as adjusted-q uncertainty.

### T11 · Transfer

A new analysis deletes genomic bins. Can the same-support stability statement be used unchanged?

1. Yes, because all topological summaries ignore support
2. No, deletion changes the object and needs its own analysis
3. Yes, provided the diagrams have the same number of points

**Answer: 2.** The theorem requires common support. Equal point counts do not restore deleted bins or the original filtration.

### T12. Transfer: same-model coverage and a failed generalization

On the same 84 sites in a second AlphaGenome track, strengthened bounds add 42 decisions while three saturation tests fail. Both bounds abstain at those exceptional sites. What is supported?

1. A new model architecture and clinical superiority were validated
2. Useful additional decision coverage transferred within one model; universal saturation did not
3. Only strengthened bounds detected all three exceptions

**Answer: 2.** The 42 added decisions occur elsewhere. Both bounds abstained at the three exceptions. The same sites and architecture prevent an independent-model or new-locus claim.

## Use the toolkit in a research workflow

The toolkit audits **finite persistence diagrams and a declared relative shift**. It does not generate AlphaGenome predictions, construct diagrams from maps, identify genomic loops, or predict variant pathogenicity.

### 1. Define the upstream comparison

Before calculating diagrams, record the map representation, genomic window, bin support, track, excluded entries, filtration direction, homology degree and coefficient field. Reference and alternate diagrams need compatible conventions.

For the study's full flag filtration with native edge births `w = -L`, subtracting a scalar `a(L)` from every map entry adds `a(L)` to both diagram coordinates. Use `delta = a(L_alt) - a(L_ref)`. For mean centering, compute each mean over the same declared off-diagonal support. Other scalar anchors can be audited by supplying their corresponding delta.

Censoring, infinite intervals, different support, pseudocounts and nonlinear transformations require their own analysis. Do not silently delete essential intervals merely to fit this input format.

### 2. Prepare a finite-diagram record

A single-site JSON record has a reference diagram, a list of alternate diagrams and one shift per alternate. `selected` is optional and only labels descriptive top credit.

```json
{
  "id": "synthetic-example",
  "reference": [[0, 4]],
  "alternates": [
    {"id": "A", "diagram": [[1, 5]], "delta": 0.25},
    {"id": "B", "diagram": [[-1, 3]], "delta": 0.25},
    {"id": "C", "diagram": [[0.5, 4.5]], "delta": 0.25}
  ],
  "selected": "B"
}
```

Coordinates must be finite, with death at least birth. Empty diagrams are valid. Preserve duplicate points because multiplicity affects matching. Use unique alternate identifiers. The browser deliberately limits diagram size for responsiveness; the Python command has a separate documented limit.

The declared delta is an input assumption. The toolkit cannot reconstruct or validate a map mean from diagram coordinates alone.

### 3. Run the audit

For the browser lab, select a synthetic preset or load a local JSON file. Inspect the directly computed distance curve, endpoint envelope, diagram shift, tolerance-defined top sets and unresolved bounds. Importing a file does not make it part of the packaged research dataset.

For Python, from a checkout:

```sh
python -m anchor_audit path/to/site.json --output path/to/report.json
```

The command also accepts a batch object containing a `sites` array. Use the command's `--help` output for path resolution, size limits, path sampling, tolerance and numerical-allowance options. Treat input and output as different files.

For a prospective study, save and hash native-only decisions before evaluating centered distances. The research IMR-90 protocol did this; a browser demonstration of both endpoints is not itself a prospectively locked experiment. Use both-endpoint envelopes for the retrospective whole-path audit and native-only intervals for prospective centered-leader decisions.

### 4. Interpret the report

| Report element | What it answers | What it does not establish |
|---|---|---|
| Native and centered distances | How the specified shift changes the computed comparison | Physical contact change or a clinical effect |
| Direct path samples | Values recomputed at the recorded fractions | Every unsampled point without an additional theorem or enclosure |
| Endpoint envelope | A path bound under the stated endpoint-error assumptions | Automatically validated floating-point error |
| Near-saturation diagnostic | Whether the computed endpoint change nearly reaches its shift bound | Exact equality for inaccessible real-valued source outputs |
| Native-margin leader | A sufficient whole-path ranking condition under the stated bounds | That the leader is biologically correct |
| Hausdorff-strengthened endpoint bounds | Whether a centered leader can be identified without using its computed centered distance for selection | A universal substitute for bottleneck matching or a measured runtime speedup |
| Selected credit | The selected label's share of the tolerance-defined top set | Predictive accuracy against independent clinical truth |
| Warnings | Invalid or unresolved parts of the supplied analysis | Permission to omit unfavorable sites |

The audit's main score is bottleneck distance. A larger score means a larger diagram discrepancy under the declared representation. It is not intrinsically a “better allele.” Choose the scientific interpretation separately.

### 5. Report enough for someone else to check it

Retain the input JSON, audit output, software version or commit, coordinate units, upstream diagram producer, delta convention, tolerance, numerical allowance and any errors. Record how sites were selected and whether comparisons were planned before outcomes were inspected.

Scale tolerance and numerical allowances whenever coordinate units change. Check more than one defensible tolerance when apparent decisiveness is the finding. Keep a fixed primary rule; label later checks as sensitivity analyses.

For larger cohorts, report the sites left unresolved, strict leaders replaced, ties introduced or resolved, alternate baselines and every failed planned evaluation. Do not choose the centering fraction to favor selected labels and then call the result predeclared.

### 6. Keep evidence classes separate

Synthetic presets verify and explain mathematical behavior. The study panel reports aggregate results from selected predicted maps. User imports are a third evidence source and must carry their own provenance.

A reusable computation helps make the method inspectable. It does not establish independence from model training, biological exchangeability, calibrated clinical performance or experimental chromosome architecture. Those require different evidence.

The paired IMR-90 study illustrates why abstention and added coverage need separate reporting: both methods abstained at all three saturation-exception sites, while strengthened bounds added 42 decisions elsewhere. The full v0.2.0 study archive supplies the map inputs separately from small scalar-verification records, with provider output notices retained.

## Further reading and source roles

The full reference list belongs to the frozen manuscript. Three particularly close methodological precedents are [Sheehy, Kisielius and Cavanna on shift-invariant bottleneck distance](https://donsheehy.net/research/cavanna18computing.pdf), [Cao and colleagues on dilation-invariant comparisons](https://academic.oup.com/imaiai/article/12/3/1964/7217093), and [May, Krishnamoorthy and Gambill on normalized bottleneck distance](https://doi.org/10.1007/s44007-024-00130-0). These delimit the claimed contribution; this companion does not independently validate their studies.

The earlier AlphaGenome reproduction package is [Zenodo 23537469](https://doi.org/10.5281/zenodo.23537469). It belongs to the retained profile audit. The current [Anchor Audit Toolkit](https://github.com/patrickiben/contact-map-anchor-audit) and [live lab](https://patrickiben.github.io/contact-map-anchor-audit/) make the new method inspectable with synthetic examples and user-supplied diagrams. The toolkit starts after persistence diagrams have been created and does not silently supply a biological anchor or source-data validation.

AlphaGenome outputs and substantial derivatives, including the genomic numerical results discussed here, remain subject to the AlphaGenome Output Terms, separate from the MIT software license. The study release includes the binding terms, required attribution, modification record, and three-part archive checksums/reassembly instructions. Saved raw maps retain their original bytes; mean centering, persistence analysis, ranking and visualization are documented processing steps.

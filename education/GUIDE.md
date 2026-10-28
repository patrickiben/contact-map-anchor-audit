# Understand the Anchor Audit

A guided route from diagram translation to a defensible ranking interpretation. Start with the browser presets, then use the worked examples and research workflow.

**Status:** educational adaptation prepared; human learner validation and author approval are not certified. The interactive questions are practice, not the original locked human transfer assessment.

## Start with the right object

A map, a diagram and a score answer different questions.

A contact map has a value for each pair of genomic bins. A persistence diagram summarizes when graph features appear and disappear as an edge threshold changes. A single aggregate score is a further summary; it cannot recover the map.

The study used predicted log-enrichment maps. These signed values are not observed read counts. The toolkit starts later in the workflow: you supply finite diagram coordinates and a declared shift. It does not request predictions or compute persistence from a contact matrix.

Keep reference and alternate bins, masks, track and filtration conventions aligned before creating diagrams. Changing that support changes the scientific comparison.

**Try it:** List which information a diagram preserves and which genomic locations it can discard.

**Boundary:** An abstract degree-one feature is not automatically a located chromatin loop.

Source: current BMC manuscript lines 35–42; see [source map](SOURCE_MAP.json).

## A stable distance can still change a rank

Small score changes and large ranking changes can coexist.

Bottleneck distance matches diagram points while allowing points to be matched to the diagonal. The cost is the largest displacement in the best matching. A point can disappear at a cost equal to half its lifetime.

On the same finite support, a bound on every edge-value change bounds the resulting diagram distance. This is a standard stability result. It does not require treating an arbitrary contact transform as a metric.

Ranks answer a different question. If two scores are tied, even a small difference can select a unique leader. A stable numerical score therefore does not guarantee a stable rank.

**Try it:** Two scores are both 1.000. One becomes 1.001. Has the score changed much? Has the unique-leader decision changed?

**Boundary:** Mathematical stability does not establish biological calibration.

Source: current BMC manuscript lines 35–42; see [source map](SOURCE_MAP.json).

## Move the origin, preserve interval lengths

Centering translates both coordinates of each interval.

For the study filtration, subtracting a map-wide mean adds that mean to every interval birth and death. The lifetime, death minus birth, stays fixed. The two maps can shift by different amounts.

Let delta be the alternate mean minus the reference mean. The audit computes the distance between the reference diagram and the alternate diagram shifted by lambda times delta. Lambda runs from zero to one. It is a preprocessing path, not a sequence or biological trajectory.

The distance can change by at most the absolute shift. Endpoint bounds enclose the intervening path. Exact equality at that bound forces a straight path; a small floating-point residual alone does not prove exact equality.

Two information settings matter. Whole-path envelopes use both native and centered endpoints after evaluation. The prospective endpoint audit instead uses native diagrams, native distances and the declared shifts before centered matching; those endpoint decisions do not automatically protect the whole path.

**Try it:** Use reference (0,4), alternate (1,5), and shift 0.25. Check that the lifetime stays 4 while distance rises from 1 to 1.25.

**Boundary:** Numerical near-saturation is not a formal certificate for unseen higher-precision model outputs.

Source: current BMC manuscript lines 43–76; see [source map](SOURCE_MAP.json).

## Leave uncertain winners unresolved

A tolerance and score bounds make the ranking rule explicit.

The top set contains every score within the chosen tolerance of the maximum. When the selected allele belongs to a tie, fractional credit divides one by the size of that top set. Ties are not silently broken by array order.

Bounds can identify possible winners, guaranteed members of the top set, and guaranteed unique leaders. A sufficient native-margin bound can protect a strict leader throughout the path. When a bound is inconclusive, the right output is an unresolved set.

A Hausdorff witness is a lower bound obtained from nearest-point or diagonal distances. It can strengthen a decision without another full matching. It can miss multiplicity constraints, so it is not a replacement for bottleneck distance.

In a locked paired IMR-90 test, simple bounds identified 7 of 84 centered leaders and strengthened bounds identified 49: 42 additional decisions across six genes, with zero observed contradictions and 35 unresolved sites. The practical numerical allowance is not a full validated-arithmetic enclosure.

**Try it:** Increase the tie tolerance in the lab. Explain why a previously unique leader can become unresolved without changing any diagram.

**Boundary:** A unique maximum is not evidence that the selected allele is clinically correct.

Source: current BMC manuscript lines 77–159; see [source map](SOURCE_MAP.json).

## Interpret the earlier AVI result precisely

A significant conditional result can have a negative observed margin.

The historical AVI counts rank Euclidean distances from a background centroid. They are not established rankings of raw AVI values. This distinction matters in a paper about anchor-sensitive rankings.

The mean statistic is the selected distance minus the larger competing distance. In the reported missense analysis the observed average was negative, but the simulated matched-null average was more negative. The significant result therefore describes enrichment relative to that null, not average superiority to the strongest alternative.

Some reported small adjusted values came from zero exceedances in a finite simulation. They are estimates at the simulation resolution floor. The frozen significant-count criterion and its remaining Monte Carlo uncertainty are both retained.

**Try it:** An observed margin is -0.01 and a simulated-null mean is -0.08. State one conclusion the difference supports and one it does not.

**Boundary:** Neither background-distance ranking nor null-relative enrichment supplies an independently validated pathogenic-versus-benign classifier.

Source: current BMC manuscript lines 195–202; see [source map](SOURCE_MAP.json).

## Separate exact arithmetic from a scientific null

The calculation can be exact while the model remains conditional.

At each site, the study compared all three non-reference substitutions. Selected-allele credit records whether the clinically selected substitution is among the top scores, with ties sharing credit.

The label tests held the computed maps fixed and used specified probabilities for which allele would be selected. Exact finite-label arithmetic computes that conditional distribution without Monte Carlo sampling error. It does not make the selection process a randomized clinical experiment.

No discovery primary or sensitivity test survived Holm adjustment across the sixteen-test family. This did not establish the absence of every biological effect. Different representations and label models answer different questions.

**Try it:** Explain why exact probability arithmetic cannot prove that clinically selected alleles were exchangeable.

**Boundary:** Null reference intervals are not biological effect confidence intervals.

Source: current BMC manuscript lines 117–128; see [source map](SOURCE_MAP.json).

## Find the mechanism before celebrating the ranking

Centering resolved many native ties without replacing strict leaders.

The discovery audit found numerical endpoint saturation across its computed allele comparisons. Some distances increased and others decreased. The sign of the response depended on relative diagram location.

Centering resolved 72 native ties while preserving all 45 strict native leaders. The observed path mechanism concerns how preprocessing changes the comparison. It does not by itself establish a useful gain in clinical discrimination.

Adding the absolute mean shift to the native distance reconstructed many centered top sets, but not all. Two diagrams can share the same native distance and shift while responding in opposite directions.

The earlier GM12878 saturation pattern did not universally transfer: 249 of 252 IMR-90 comparisons passed and three RB1 comparisons failed. Both simple and strengthened bounds already abstained at all three sites. The distinct witness gain is 42 decisions elsewhere, not unique detection of these exceptions. Exploratory direct samples showed two turning paths and one effectively flat path.

**Try it:** Compare alternates (1,5) and (-1,3) against reference (0,4), with the same positive shift. Why does the scalar native distance not tell you the direction?

**Boundary:** Local saturation is ordinary on a nonflat piece of a finite matching problem; its frequency is not a new generic theorem.

Source: current BMC manuscript lines 160–194; see [source map](SOURCE_MAP.json).

## Ask what actually replicated

More unique ranks did not produce a consistent clinical-credit gain.

The new spatial cohort and protocol were fixed before those maps were acquired. It contained 84 sites in seven other loci. New spatial outcomes were prospective; independence from model training was not established.

All 66 native ties became unique maxima, and all 18 strict native leaders were preserved. Yet selected-allele credit fell descriptively from about 0.359 to 0.321. The sharper ranks and the selected-label outcome therefore moved in different directions.

The stronger witness bounds identified additional endpoint leaders beyond the simple margin check. This measures decision yield. A runtime speedup was not benchmarked, and no new confirmatory clinical-enrichment test was added.

IMR-90 reused the same 84 replication sites and the same AlphaGenome architecture. Its protocol preceded acquisition; native-only predictions were locked before centered distances were evaluated. GM12878 witness increments had been compared after those outcomes. A second output track adds neither independent loci nor an independent model.

IMR-90 selected credit rose descriptively from 0.335317 to 0.398810, whereas GM12878 replication credit fell. Native and centered RMS credits were 0.500000 and 0.517857 in IMR-90 and 0.444444 and 0.460317 in GM12878; all exceeded centered H1 in the corresponding track. More unique rankings did not establish clinical superiority.

**Try it:** Give a one-sentence conclusion that includes both tie resolution and the credit decrease.

**Boundary:** Eighty-four overlapping windows do not represent 84 independent genomic regions.

Source: current BMC manuscript lines 98–173; see [source map](SOURCE_MAP.json).

## Match the conclusion to numerical resolution

Tolerance, delivered precision and solver error have distinct roles.

The delivered map values lie on a finite precision grid. This makes resolution relevant to ties, but does not isolate quantization as the cause of every tie or saturation event. Higher-precision source predictions would be needed for that comparison.

A tie tolerance defines an analysis convention. A numerical allowance is a claimed budget for computation error. Neither automatically becomes a physical detection limit. If coordinate units change, both must be scaled with the scores.

The paper reports numerical witnesses using practical allowances. It does not provide a complete interval-arithmetic certificate for every solver operation. The software likewise distinguishes numerical checks from formal real-arithmetic proof.

**Try it:** Multiply all diagram coordinates and shifts by ten. What else must be multiplied by ten to preserve the same ranking rule?

**Boundary:** Reproducing floating-point outputs does not reveal the model’s unexposed internal precision.

Source: current BMC manuscript lines 129–136; see [source map](SOURCE_MAP.json).

## Use reproducibility to answer the right question

A rerun supports computation; independent measurements support biology.

The validation reran cached-input calculations and checked source-specific numerical claims. Replaying original random seeds can reproduce a simulation exactly without reducing its statistical uncertainty.

This toolkit adds synthetic examples and reusable software. Imported diagrams are processed locally in the browser. The study-summary panel reports aggregate author analyses, not raw contact maps.

The research contribution combines a specified preprocessing path, ranking bounds, useful witnesses, explicit unresolved cases and measured new-locus behavior. It is not a new generic distance, a physical loop detector or a clinical prediction tool.

The full v0.2.0 study archive is publicly released with the manuscript, code and verification records. Toolkit code is MIT-licensed; model outputs retain separate provider terms and attribution. Public release does not establish clinical validity, author journal approval or human learner transfer.

Declarations confirm no competing financial or nonfinancial interests and no specific grant or institutional funding. Codex assisted the work; Qwen3.8 earlier drafting; Qwen3.8-Max author-supplied QC checked against retained artifacts. AI checks are not external peer review; final author approval remains pending.

**Try it:** Describe one independent measurement that would be needed to connect the audit to a real structural chromosome change.

**Boundary:** The practice quiz has not been validated with human learners and does not replace author review.

Source: current BMC manuscript lines 203–274; see [source map](SOURCE_MAP.json).

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

## Keep these distinctions

- Synthetic presets are teaching examples, not genomic observations.
- The toolkit does not infer pathogenicity or locate chromatin loops.
- Numerical near-saturation is not formal real-arithmetic certification.
- Aggregate study results concern two output tracks of one model, reusing the same 84 sites in the paired test.
- The interactive quiz is practice with answer feedback, not a validated human transfer assessment.
- Public release authorization is not a human learner or author journal-approval verdict.

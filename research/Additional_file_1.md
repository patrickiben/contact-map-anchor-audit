# Additional file 1: Vertex thinning

Retained mathematical contribution from the combined manuscript. Vertex thinning deletes bins and is distinct from sequencing-depth reduction. The numbering below belongs to this supplement.



**Proposition 2: finite-set degree-one extinction.** Fix $N$ bins and retain each independently with probability $p$. Restrict the edge array to the retained bins and use the weighted flag filtration defined in the main text. Let $T_p$ be a well-defined statistic that equals zero whenever the resulting degree-one diagram is empty. Transformations of the statistic or filtration may depend on $p$ or the retained count, provided they preserve this zero. Then, for every $\varepsilon > 0$,

$$\Pr(|T_p|>\varepsilon)\leq\Pr\{\operatorname{Bin}(N,p)\geq4\}\leq \binom{N}{4}p^4.$$

**Proof.** A flag complex on at most three vertices has no degree-one homology: any three-cycle is filled by its triangle. A nonempty degree-one diagram therefore requires at least four retained vertices. If $K$ is the retained count, the indicator of $K \geq  4$ is bounded by the number of retained four-vertex subsets, whose expectation is $\binom{N}{4}p^4$. This proves the bound and convergence to zero in probability for fixed $N$.

The result concerns the probability of a nonzero statistic. It does not give a universal exponent for persistence amplitude, an expectation bound for arbitrarily rescaled statistics, or a monotonicity law at finite $p$. Deleting the hub of a wheel graph can expose a four-cycle and increase degree-one persistence. Complexes with at most three vertices need not be contractible; the proof requires only their empty degree-one diagrams.

If $N$ grows, $p$ tending to zero alone is insufficient. Vanishing expected retained count, $Np \to  0$, is sufficient for extinction. Four growing groups arranged around a cycle can retain a degree-one feature when each group still contains retained vertices. Consequently, the finite-set argument must not be presented as an impossibility theorem for ordinary sequencing-depth changes at fixed bin resolution.

Subsampling a retained set to a fixed $m$ bins is available only when at least $m$ remain. For a fixed original bin set and map, under independent retention with a common probability $p$, conditional on eligibility and averaging over the retained set, a subsequent uniform $m$-subset is uniformly distributed among the original $m$-subsets. This yields a specific conditional comparability statement; it does not recover the full-map target or remove the loss of eligibility. The proof supplies the finite-sampling boundary directly. It provides no planar scaling exponent for contact-map summaries.


**Map-specific refinement.** Let $a_j$ count $j$-bin subsets whose restricted full filtration has a positive-length H1 interval. Independent vertex retention gives the exact finite expression

$$\Pr\{D_1(w|R_p)\ne\varnothing\}=\sum_{j=4}^N a_jp^j(1-p)^{N-j}.$$

If $k$ is the smallest index with $a_k > 0$, its leading term is $a_k p^k + O(p^{k+1})$ for fixed map and $N$. If all $a_j$ vanish, the probability is zero. Thus the universal fourth-power upper bound is sharp in order only when the map contains a four-bin witness. A five-cycle with perimeter births zero and all chord births one has probability exactly $p^5$. Additional retained vertices may fill a witness, so the event is not monotone. This refinement concerns diagram nonemptiness; a particular statistic can still vanish on a nonempty diagram. Exhaustive four- and five-cycle checks accompany the proof.


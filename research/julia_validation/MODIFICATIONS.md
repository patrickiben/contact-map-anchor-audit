# Targeted Julia-check modifications

This capsule selects nine previously studied sites on both tracks. The 38 files under study_inputs are exact copies of the original maps, site-analysis records and two GM12878 bound/witness records; their source hashes are recorded. Exported input matrices convert saved Float32 contact values to Float64 storage without changing their values. Julia computes complete persistence diagrams from shifted Float32 edge inputs, restores the offset and sorts intervals without removing multiplicities. New downstream calculations recompute distances, witnesses and rankings. These operations are scientific transformations of AlphaGenome outputs, not new experimental observations.

Raw maps and substantial derived numerical files retain the included AlphaGenome Output Terms, separate from the MIT license for original code. No model weights, credentials, waiver application, financial circumstances or private submission correspondence are included.

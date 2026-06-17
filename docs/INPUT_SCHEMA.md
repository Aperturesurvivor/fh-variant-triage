# Input Schema

This project has two main data-entry paths:

1. The built-in ClinVar pipeline, which uses NCBI ClinVar
   `variant_summary.txt.gz`.
2. The bring-your-own CSV scorer, `scripts/score_variants_csv.py`.

## Bring-Your-Own CSV

Run:

```bash
python scripts/score_variants_csv.py examples/example_variants.csv reports/example_scored_variants.csv
```

The CSV must describe variants in one of the supported FH genes:

- `LDLR`
- `APOB`
- `PCSK9`

Rows containing other genes are rejected.

## Accepted Columns

### Required In Practice

At least one gene column is required:

| Canonical column | Alias | Meaning |
| --- | --- | --- |
| `GeneSymbol` | `gene` | Supported FH gene symbol: `LDLR`, `APOB`, or `PCSK9`. |

At least one variant-description column is strongly recommended:

| Canonical column | Alias | Meaning |
| --- | --- | --- |
| `Name` | `variant_name` | HGVS-like or readable variant name. Used to infer simple variant class and name length. |

### Optional But Useful

| Canonical column | Alias | Meaning |
| --- | --- | --- |
| `Type` | none | ClinVar-like variant type, such as `single nucleotide variant`, `Deletion`, or `Duplication`. |
| `MolecularConsequence` | `molecular_consequence` | Sequence Ontology-like consequence, such as `missense_variant` or `frameshift_variant`. |
| `ClinicalSignificance` | none | Existing label if known; preserved in output but not required for scoring. |
| `VariationID` | none | ClinVar variation identifier if available. |
| `PhenotypeList` | none | Existing phenotype text if available. |

### Derived Columns

If these are absent, the scorer derives them:

| Column | How it is derived |
| --- | --- |
| `variant_type_simple` | Parsed from `Name`; values include `substitution`, `deletion`, `duplication`, `insertion`, `delins`, `other`. |
| `is_lof_like` | String search over name/type/consequence for loss-of-function-like terms. |
| `name_length` | Character length of `Name`. |

## Output Columns

The output preserves input/normalized columns and adds:

| Column | Meaning |
| --- | --- |
| `pathogenic_bucket_score` | Prototype probability-like score for resembling ClinVar pathogenic/likely pathogenic records. |
| `triage_band` | `high_priority_review`, `moderate_priority_review`, `watchlist`, or `lower_priority`. |

## Interpretation Boundary

Scores are research triage signals. They are not diagnoses, not ACMG/ClinGen
classifications, and not person-level probabilities of FH.


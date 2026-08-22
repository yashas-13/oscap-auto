# Benchmark Registry

This directory contains versioned metadata for security benchmarks, regulatory profiles, frameworks, and threat-intelligence sources used by oscap-auto.

## Principles

- Keep benchmark metadata separate from proprietary benchmark documents.
- Record the official source and version for every dataset.
- Treat `status: current` as a registry assertion, not a substitute for upstream verification.
- Preserve license information and do not redistribute restricted benchmark content without permission.
- Regulations such as CERT-In, DPDP, RBI, SEBI and IRDAI are tracked as continuously-updated sources rather than static executable benchmarks.

## Object types

- `benchmark`: executable security baseline such as CIS.
- `regulation`: legal/regulatory requirement.
- `sector-regulation`: sector-specific requirement.
- `framework`: control/risk framework such as NIST CSF or ISO/IEC 27001.
- `threat-intelligence`: adversary knowledge such as MITRE ATT&CK.

## Verification

Run the registry tests with:

```bash
python -m pytest tests/benchmark_registry_test.py
```

The tests validate schema presence and core platform coverage. They do not claim that an upstream source remains latest; an upstream refresh process should update the registry when official releases change.

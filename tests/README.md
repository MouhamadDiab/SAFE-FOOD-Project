# Tests

Run after the local graph has been generated:

```
python -m pytest tests -q
```

If `pyshacl` is installed, the negative-energy test checks that the real SHACL validator returns nonconformance. Without it, the test still checks invalid data is not pre-filtered, then marks the pySHACL verification as skipped; it never claims SHACL was tested. The CI pipeline installs `pyshacl` and executes this test.

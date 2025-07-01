# Unit Tests

This directory is for unit tests of the hetu-pycli Python modules.

- Unit tests should focus on individual functions, classes, and logic, not full CLI flows.
- Use pytest for all unit tests.
- Mock external dependencies (e.g., web3, file IO) where possible.
- Place test files as `test_*.py`.

Example test files:
- `test_wallet.py`: Test wallet keystore logic, encryption/decryption, etc.
- `test_erc20.py`: Test ERC20 contract wrapper logic.

See `../e2e_tests/README.md` for E2E test guidelines.

## Running Unit Tests

To run the unit tests, ensure you have the Hetu CLI installed and configured. Then, execute:

```bash
poetry run pytest tests/unit_tests
```
This will discover and run all tests in the `tests/unit_tests` directory.

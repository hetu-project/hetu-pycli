# End-to-End Tests

This directory is for end-to-end (E2E) tests of the hetu-pycli CLI and its integration with the Hetu/Ethereum chain.

- E2E tests should simulate real user scenarios, such as wallet creation, contract interaction, and transaction signing/broadcasting.
- Tests may use subprocess to invoke CLI commands, or pytest + Typer's CliRunner for CLI testing.
- You may need a testnet RPC and test accounts for full E2E coverage.

Example test files:
- `test_wallet_e2e.py`: Test wallet create/import/export/unlock via CLI.
- `test_erc20_e2e.py`: Test ERC20 contract commands via CLI.

See `../unit_tests/README.md` for unit test guidelines.

## Running E2E Tests

To run the E2E tests, ensure you have the Hetu CLI installed and configured with a testnet RPC endpoint. Then, execute:

```bash
poetry run pytest tests/e2e_tests
```
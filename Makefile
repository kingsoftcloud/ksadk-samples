.PHONY: validate test public-scan public-preflight

validate:
	uv run python scripts/validate_samples.py

test:
	uv run pytest -q

public-scan:
	uv run python scripts/check_public_readiness.py

public-preflight: public-scan validate test

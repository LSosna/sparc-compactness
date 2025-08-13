.PHONY: env run samples stats fit all

env:
	pip install -r requirements.txt

run:
	PYTHONPATH=. python scripts/run_all.py

samples:
	PYTHONPATH=. python scripts/make_samples.py

stats:
	PYTHONPATH=. python scripts/summary_stats.py

fit:
	PYTHONPATH=. python scripts/fit_mass_compactness.py

all: env run samples stats fit
	@echo "Done. See outputs/summary/ and outputs/tables/"

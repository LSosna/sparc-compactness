.PHONY: all env run samples stats fit clean

env:
\tpip install -r requirements.txt

run:
\tPYTHONPATH=. python scripts/run_all.py

samples:
\tPYTHONPATH=. python scripts/make_samples.py

stats:
\tPYTHONPATH=. python scripts/summary_stats.py

fit:
\tPYTHONPATH=. python scripts/fit_mass_compactness.py

all: env run samples stats fit
\t@echo "Done. See outputs/summary/ and outputs/tables/"

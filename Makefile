COURSES := sc2005 sc2008 sc3000 sc4001 sc4002 sc4061
MANAGED_TEXLIVE_BIN := $(dir $(firstword $(wildcard $(HOME)/.cache/codex-runtimes/codex-texlive/full/bin/*/latexmk)))

ifneq ($(MANAGED_TEXLIVE_BIN),)
export PATH := $(MANAGED_TEXLIVE_BIN):$(PATH)
endif

.PHONY: all $(COURSES)

all: $(COURSES)

$(COURSES):
	@mkdir -p build/$@
	@if command -v latexmk >/dev/null 2>&1; then \
		cd courses/$@ && latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../../build/$@ main.tex; \
	elif command -v tectonic >/dev/null 2>&1; then \
		cd courses/$@ && tectonic -X compile --outdir ../../build/$@ main.tex; \
	else \
		echo "No supported LaTeX toolchain found. Install latexmk + XeLaTeX, or Tectonic."; \
		exit 1; \
	fi

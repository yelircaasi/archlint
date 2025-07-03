TESTDIR := "tests"
PROJECTCACHE := ".cache"
COV_HTML_DIR := "{{PROJECTCACHE}}/coverage/coverage_html"
COVERAGE_ARGS := "--cov --cov-config=pyproject.toml --cov-report=term:skip-covered --cov-report=html"
COVERAGE_ARGS_ := "--cov=archlint --cov-config=pyproject.toml --cov-report=term:skip-covered --cov-fail-under=0 --cov-report=html:codeqa/coverage/html"
TESTMON_PREFIX := 'TESTMON_DATAFILE=".cache/testmondata"'
PROFILING_ARGS := ""
PROFILING_ARGS_ := "--profile --profile-svg --pstats-dir .cache/prof --element-number 0"
TEST_CFG_ARG := "--config-file=pyproject.toml"
TESTMON_ARGS := "--testmon --testmon-forceselect --no-cov"
STOP_FORWARDING := "python ./scripts/stop_port_forwarding.py"
TIMESTAMP := 'date +"%Y-%m-%d %H:%M:%S.%3N"'
VIEWER := "$BROWSER"

alias mypy := typecheck
alias l := lint
alias d := docs
alias tc := test-cov
alias t := test
alias ct := check-tests
alias cd := check-docs
alias cmo := check-method-order
alias ci := check-imports
alias flame := flamegraph
alias perf := perf-flamegraph

default:
    just --list

commit:
    treefmt
    cz commit

format:
    treefmt

check:
    ruff check .

fix:
    ruff check --fix .

typecheck path="$PWD":
    mypy --cache-dir .cache/mypy_cache {{ path }}
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_mypy

lint path="$PWD": format typecheck fix deal
    yamllint -c codeqa/configs/yamllint.yml codeqa/ mkdocs.yml lefthook.yml 

deal:
    python -m deal lint

@vulture:
    vulture

pydeps-full:
    pydeps src/archlint \
        --noshow \
        -T svg \
        --show-deps \
        --pylib \
        -o codeqa/dependencies/pydeps/archlint-full.svg \
        --rmprefix archlint. \
        > codeqa/dependencies/pydeps/pydeps-full.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_pydeps_full

pydeps:
    pydeps src/archlint \
        --noshow \
        -T svg \
        --show-deps \
        -o codeqa/dependencies/pydeps/archlint.svg \
        --rmprefix archlint. \
        --cluster \
        --max-module-depth 3 \
        > codeqa/dependencies/pydeps/pydeps.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_pydeps

pydeps-simple:
    pydeps src/archlint \
        --noshow \
        -T svg \
        --show-deps \
        -o codeqa/dependencies/pydeps/archlint-simple.svg \
        --cluster \
        --max-module-depth 2 \
        > codeqa/dependencies/pydeps/pydeps-simple.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_pydeps_simple

@view-deps:
    echo "Recency:"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps_full`"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps`"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps_simple`"
    {{ VIEWER }} `pwd`/codeqa/dependencies &>/dev/null

snakefood:
    python -m snakefood3 src/ archlint \
        --group codeqa/dependencies/snakefood/group.txt \
        > codeqa/dependencies/snakefood/archlint.dot
    sed -i 's/dpi="150",/size="25,25!",\n            dpi="50",/' codeqa/dependencies/snakefood/archlint.dot
    dot -T svg \
        codeqa/dependencies/snakefood/archlint.dot \
        -o codeqa/dependencies/snakefood/archlint.svg
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_snakefood

deply:
    deply analyze \
        --config codeqa/dependencies/deply/deply.yaml \
        --output codeqa/dependencies/deply/report.txt \
        --report-format text
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_deply

bandit:
    bandit -r src/archlint/ --baseline codeqa/security/bandit/baselines/archlint.json
    bandit -r scripts/ --baseline codeqa/security/bandit/baselines/scripts.json

bandit-html:
    bandit -r src/archlint/ --format html --output codeqa/security/bandit/archlint.html --baseline codeqa/security/bandit/baselines/archlint.json
    bandit -r scripts/ --format html --output codeqa/security/bandit/scripts.html --baseline codeqa/security/bandit/baselines/scripts.json

view-bandit:
    {{ VIEWER }} codeqa/security/bandit

pyflame:
    python -m pyflame \
        --output-path codeqa/performance/pyflame/flamegraph.svg \
        scripts/wrapper_pyflame.py

flamegraph:
    flamegraph -o codeqa/performance/flamegraph/flamegraph.svg -- archlint

perf-flamegraph:
    sh scripts/perf-flamegraph.sh

view-flamegraphs:
    {{ VIEWER }} `pwd`/codeqa/performance &>/dev/null

check-docs:
    archlint docs
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_check_doc_structure

check-tests:
    archlint tests
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_check_test_structure

check-imports:
    archlint imports
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_check_imports

check-method-order:
    archlint methods
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_check_method_order

smoke:
    pytest {{ TEST_CFG_ARG }} tests/smoke

test:
    {{ TESTMON_PREFIX }} pytest {{ TEST_CFG_ARG }} {{ TESTMON_ARGS }} {{ TESTDIR }} \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_partial \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

unit:
    {{ TESTMON_PREFIX }} pytest tests/unit {{ TEST_CFG_ARG }} {{ TESTMON_ARGS }} {{ TESTDIR }} \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_partial \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

test-cov:
    pytest {{ TEST_CFG_ARG }} {{ COVERAGE_ARGS }} {{ TESTDIR }}/ \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_all \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

@view-cov:
    echo "Recency: `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_test`"
    {{ VIEWER }} `pwd`/codeqa/coverage/html/index.html &>/dev/null

docs:
    mkdocs build

docs-lazy:
    python scripts/lazy_mkdocs.py
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_docs

serve-docs:
    mkdocs serve

@view-docs:
    echo "Recency: `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_docs`"
    {{ VIEWER }} `pwd`/docs/site/index.html &>/dev/null

sbom:
    uv export --format requirements.txt > requirements.txt
    cyclonedx-py requirements > sbom.json
    python scripts/jsonfmt.py 4 sbom.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_sbom

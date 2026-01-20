# Sprint 16 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 16 (Days 0-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint Goal:** Reporting Infrastructure, Gap Analysis & Targeted Parser/Solve Improvements

**Key Deliverables:**
- Reporting infrastructure with `generate_report.py` CLI
- Automated status and failure analysis reports
- Grammar extensions for parsing improvements
- emit_gams.py fixes for solve improvements
- Progress tracking with sprint comparison

**Prep Phase Complete:** All 10 prep tasks done, 27/27 unknowns verified (100%)

**Success Criteria:**
| Metric | Baseline (Sprint 15) | Minimum | Target | Stretch |
|--------|----------------------|---------|--------|---------|
| Parse Success Rate | 21.3% (34/160) | 31.3% (+16) | 37.5% (+26) | 49.4% (+45) |
| Solve Success Rate | 17.6% (3/17) | 60% (10/17) | 76% (13/17) | 100% (17/17) |
| Full Pipeline Success | 0.6% (1/160) | 3% (5/160) | 5% (8/160) | 8% (13/160) |

---

## Day 0 Prompt: Sprint Setup and Preparation

**Branch:** Create a new branch named `sprint16-day0-setup` from `main`

**Objective:** Set up Sprint 16 infrastructure, create sprint log, and verify all prerequisites are in place.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` - Full sprint plan with 10-day schedule
- Read `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - All 27 verified unknowns
- Read `docs/planning/EPIC_3/SPRINT_16/SPRINT_SCHEDULE.md` - Day-by-day schedule and success criteria
- Review Sprint 15 deliverables:
  - `tests/output/baseline_metrics.json` - Sprint 15 baseline metrics
  - `tests/output/pipeline_results.json` - Per-model pipeline results
  - `scripts/gamslib/error_taxonomy.py` - 47-category error classification

**Tasks to Complete (1-2 hours):**

1. **Verify Sprint 15 Deliverables** (30 min)
   - Confirm `tests/output/baseline_metrics.json` exists with Sprint 15 metrics
   - Confirm `tests/output/pipeline_results.json` exists with 160 models
   - Confirm `scripts/gamslib/run_full_test.py` runs: `python scripts/gamslib/run_full_test.py --help`
   - Confirm `scripts/gamslib/error_taxonomy.py` runs: `python -c "from scripts.gamslib.error_taxonomy import *"`
   - Confirm parse rate is 21.3% (34/160), solve rate is 17.6% (3/17)

2. **Verify Development Environment** (15 min)
   - Run: `make typecheck` - Must pass
   - Run: `make lint` - Must pass
   - Run: `make test` - All tests must pass
   - Verify Jinja2 and tabulate will be available (to add on Day 1)

3. **Create Sprint Log** (30 min)
   - Create `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
   - Include header with sprint goal, dates, and key metrics to track
   - Add Day 0 entry with setup verification results
   - Use template from `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md`

4. **Review Prep Task Deliverables** (30 min)
   - Review `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - Reporting architecture
   - Review `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` - Parse fix strategies
   - Review `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md` - Solve fix strategies
   - Review `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md` - Safe grammar patterns
   - Note any gaps or concerns

**Deliverables:**
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md` created
- All Sprint 15 dependencies verified
- Development environment confirmed working

**Quality Checks:**
No code changes expected on Day 0. If any Python files are modified:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Sprint 15 baseline metrics accessible (21.3% parse, 17.6% solve)
  - [ ] Sprint 15 pipeline scripts run without errors
  - [ ] Development environment passes quality checks
  - [ ] Sprint log created with Day 0 entry
  - [ ] All prep task documents reviewed
- [ ] Mark Day 0 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Update after PR merge with PR entry
  - See `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` for templates

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 16 Day 0: Sprint Setup and Preparation" \
                --body "Completes Day 0 tasks from Sprint 16 PLAN.md. Verifies all Sprint 15 dependencies and creates sprint log." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (full document)
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Summary Statistics section)
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_SCHEDULE.md` (Success Criteria section)
- `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` (SPRINT_LOG template)

---

## Day 1 Prompt: Module Setup and Data Loading

**Branch:** Create a new branch named `sprint16-day1-reporting-module` from `main`

**Objective:** Create reporting module structure and implement data loading for baseline_metrics.json and pipeline_results.json.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 68-95 (Day 1 details)
- Read `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - Reporting architecture and data loader design
- Read `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md` - Data structures for failure analysis
- Review Unknowns 1.1-1.4 in `KNOWN_UNKNOWNS.md` (report format, metrics, template system, historical data)
- Review `tests/output/baseline_metrics.json` - Data structure to load
- Review `tests/output/pipeline_results.json` - Per-model results structure

**Tasks to Complete (6 hours):**

1. **Create `src/nlp2mcp/reporting/` structure** (1h)
   - Create `src/nlp2mcp/reporting/__init__.py`
   - Create `src/nlp2mcp/reporting/analyzers/__init__.py`
   - Create `src/nlp2mcp/reporting/renderers/__init__.py`
   - Create `src/nlp2mcp/reporting/templates/` directory
   - Add Jinja2 and tabulate to `pyproject.toml` dependencies:
     ```toml
     dependencies = [
         # ... existing deps ...
         "Jinja2>=3.1.0",
         "tabulate>=0.9.0",
     ]
     ```
   - Run: `pip install -e .` to install new dependencies

2. **Implement `data_loader.py`** (2h)
   - Create `src/nlp2mcp/reporting/data_loader.py`
   - Implement `load_baseline_metrics(path: Path) -> BaselineMetrics`
   - Implement `load_pipeline_results(path: Path) -> PipelineResults`
   - Add data validation (check required fields, valid values)
   - Handle missing files gracefully with clear error messages
   - Use dataclasses or TypedDict for type safety
   - Reference REPORT_DESIGN.md Section "Data Loading" for schema

3. **Implement `StatusAnalyzer` class** (2h)
   - Create `src/nlp2mcp/reporting/analyzers/status_analyzer.py`
   - Implement `StatusAnalyzer.__init__(baseline: BaselineMetrics, results: PipelineResults)`
   - Implement `get_parse_rate() -> float` - Parse success rate
   - Implement `get_translate_rate() -> float` - Translation success rate (of parsed)
   - Implement `get_solve_rate() -> float` - Solve success rate (of translated)
   - Implement `get_pipeline_rate() -> float` - Full pipeline success rate
   - Implement `get_summary() -> StatusSummary` - All rates in one object
   - Reference Unknown 1.2 for metrics to extract

4. **Write unit tests for data loading** (1h)
   - Create `tests/unit/reporting/__init__.py`
   - Create `tests/unit/reporting/test_data_loader.py`
   - Test loading valid baseline_metrics.json
   - Test loading valid pipeline_results.json
   - Test handling of missing files
   - Test handling of malformed JSON
   - Create `tests/unit/reporting/test_status_analyzer.py`
   - Test rate calculations with known data
   - Run: `pytest tests/unit/reporting/ -v`

**Deliverables:**
- `src/nlp2mcp/reporting/__init__.py`
- `src/nlp2mcp/reporting/data_loader.py`
- `src/nlp2mcp/reporting/analyzers/__init__.py`
- `src/nlp2mcp/reporting/analyzers/status_analyzer.py`
- Unit tests in `tests/unit/reporting/`
- Updated `pyproject.toml` with Jinja2, tabulate dependencies

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `reporting/` module importable: `from nlp2mcp.reporting import data_loader`
  - [ ] Can load baseline_metrics.json without errors
  - [ ] Can load pipeline_results.json without errors
  - [ ] StatusAnalyzer extracts parse/translate/solve rates correctly
  - [ ] Data validation catches malformed input
  - [ ] Unit tests pass (8+ test cases)
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Update after PR merge with PR entry
  - Document any key decisions (e.g., dataclass vs TypedDict choice)

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 1: Reporting Module Setup and Data Loading" \
                --body "Creates reporting module structure with data_loader.py and StatusAnalyzer. Adds Jinja2 and tabulate dependencies." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 68-95)
- `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` (Data Loading section)
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Unknowns 1.1-1.4)
- `tests/output/baseline_metrics.json` (data structure reference)

---

## Day 2 Prompt: Analyzers and Templates

**Branch:** Create a new branch named `sprint16-day2-analyzers-templates` from `main`

**Objective:** Implement FailureAnalyzer and ProgressAnalyzer classes, create Jinja2 templates for status and failure reports.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 97-126 (Day 2 details)
- Read `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - Template design section
- Read `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md` - Failure grouping and priority scores
- Review Unknowns 2.1-2.3 in `KNOWN_UNKNOWNS.md` (failure grouping, examples, recommendations)
- Review Unknown 4.3 in `KNOWN_UNKNOWNS.md` (prioritization framework: Priority Score = Models / Effort)
- Review `scripts/gamslib/error_taxonomy.py` - Error categories to use

**Tasks to Complete (6.5 hours):**

1. **Implement `FailureAnalyzer` class** (2h)
   - Create `src/nlp2mcp/reporting/analyzers/failure_analyzer.py`
   - Implement `FailureAnalyzer.__init__(results: PipelineResults)`
   - Implement `get_parse_failures() -> dict[str, list[str]]` - Group by error category
   - Implement `get_translate_failures() -> dict[str, list[str]]` - Group by error category
   - Implement `get_solve_failures() -> dict[str, list[str]]` - Group by error category
   - Implement `calculate_priority_score(category: str) -> float` - Models / Effort (from Unknown 4.3)
   - Implement `get_prioritized_improvements() -> list[ImprovementItem]` - Sorted by priority score
   - Use error categories from `scripts/gamslib/error_taxonomy.py`

2. **Implement `ProgressAnalyzer` class** (2h)
   - Create `src/nlp2mcp/reporting/analyzers/progress_analyzer.py`
   - Implement `ProgressAnalyzer.__init__(current: BaselineMetrics, previous: BaselineMetrics | None)`
   - Implement `get_rate_deltas() -> RateDeltas` - Change in parse/translate/solve rates
   - Implement `get_model_changes() -> ModelChanges` - Newly passing/failing models
   - Implement `detect_regressions() -> list[Regression]` - Models that went from pass to fail
   - Implement `get_comparison_summary() -> ComparisonSummary` - Full comparison object
   - Reference Unknown 3.1, 3.2 in KNOWN_UNKNOWNS.md for schema design

3. **Create Jinja2 template directory** (0.5h)
   - Create `src/nlp2mcp/reporting/templates/`
   - Create `src/nlp2mcp/reporting/templates/__init__.py` (empty, for package)
   - Verify templates can be loaded: `from jinja2 import Environment, PackageLoader`

4. **Create `status_report.md.j2` template** (1h)
   - Create `src/nlp2mcp/reporting/templates/status_report.md.j2`
   - Include header with generation timestamp and version
   - Include summary table with parse/translate/solve/pipeline rates
   - Include model counts per stage
   - Include timing statistics (mean, median, p90)
   - Use tabulate for table formatting
   - Reference REPORT_DESIGN.md for layout

5. **Create `failure_report.md.j2` template** (1h)
   - Create `src/nlp2mcp/reporting/templates/failure_report.md.j2`
   - Include header with generation timestamp
   - Include parse failures grouped by category with counts
   - Include translate failures grouped by category
   - Include solve failures grouped by category
   - Include prioritized improvement recommendations
   - Include example error messages for top categories
   - Reference FAILURE_REPORT_SCHEMA.md for structure

**Deliverables:**
- `src/nlp2mcp/reporting/analyzers/failure_analyzer.py`
- `src/nlp2mcp/reporting/analyzers/progress_analyzer.py`
- `src/nlp2mcp/reporting/templates/status_report.md.j2`
- `src/nlp2mcp/reporting/templates/failure_report.md.j2`
- Unit tests for FailureAnalyzer and ProgressAnalyzer

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] FailureAnalyzer groups errors by category correctly
  - [ ] FailureAnalyzer calculates priority scores (models/effort)
  - [ ] ProgressAnalyzer computes deltas between snapshots
  - [ ] ProgressAnalyzer detects regressions
  - [ ] Templates render sample data correctly (test with mock data)
  - [ ] Templates use tabulate for tables
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Document template design decisions

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 2: Analyzers and Jinja2 Templates" \
                --body "Implements FailureAnalyzer, ProgressAnalyzer, and Jinja2 templates for status and failure reports." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 97-126)
- `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` (Template Design section)
- `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md`
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Unknowns 2.1-2.3, 3.1-3.2, 4.3)

---

## Day 3 Prompt: CLI and Integration

**Branch:** Create a new branch named `sprint16-day3-cli-integration` from `main`

**Objective:** Complete CLI tool with MarkdownRenderer and generate first automated reports.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 128-161 (Day 3 details)
- Read `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - CLI design section
- Review Day 1 and Day 2 deliverables (data_loader, analyzers, templates)
- Review Unknown 1.3 in `KNOWN_UNKNOWNS.md` (template system choice - Jinja2)

**Tasks to Complete (5.5 hours):**

1. **Implement `MarkdownRenderer` class** (1.5h)
   - Create `src/nlp2mcp/reporting/renderers/markdown_renderer.py`
   - Implement `MarkdownRenderer.__init__(template_dir: Path)`
   - Implement `render_status_report(data: StatusSummary) -> str`
   - Implement `render_failure_report(data: FailureAnalysis) -> str`
   - Implement `render_to_file(content: str, output_path: Path) -> None`
   - Use Jinja2 Environment with PackageLoader
   - Add error handling for missing templates

2. **Implement `generate_report.py` CLI** (1.5h)
   - Create `src/nlp2mcp/reporting/generate_report.py`
   - Add argparse with:
     - `--type` (required): `status`, `failure`, or `all`
     - `--output` (optional): Output directory (default: `docs/testing/`)
     - `--baseline` (optional): Path to baseline_metrics.json
     - `--results` (optional): Path to pipeline_results.json
     - `--format` (optional): `markdown` (default), future: `json`, `html`
   - Wire up data_loader, analyzers, and renderer
   - Add `if __name__ == "__main__"` entry point
   - Add to pyproject.toml scripts:
     ```toml
     [project.scripts]
     nlp2mcp-report = "nlp2mcp.reporting.generate_report:main"
     ```

3. **Integration testing** (1.5h)
   - Create `tests/integration/test_generate_report.py`
   - Test CLI with `--type=status` generates valid markdown
   - Test CLI with `--type=failure` generates valid markdown
   - Test CLI with `--type=all` generates both reports
   - Test output file creation in specified directory
   - Test with actual baseline_metrics.json and pipeline_results.json
   - Run: `pytest tests/integration/test_generate_report.py -v`

4. **Generate first reports** (0.5h)
   - Run: `python -m nlp2mcp.reporting.generate_report --type=all --output=docs/testing/`
   - Verify `docs/testing/GAMSLIB_STATUS.md` generated correctly
   - Verify `docs/testing/FAILURE_ANALYSIS.md` generated correctly
   - Review reports for accuracy (compare with baseline_metrics.json)

5. **Update pyproject.toml** (0.5h)
   - Add CLI entry point
   - Verify package installs correctly: `pip install -e .`
   - Test CLI: `nlp2mcp-report --help`

**Deliverables:**
- `src/nlp2mcp/reporting/renderers/markdown_renderer.py`
- `src/nlp2mcp/reporting/generate_report.py` (CLI entry point)
- Generated `docs/testing/GAMSLIB_STATUS.md`
- Generated `docs/testing/FAILURE_ANALYSIS.md`
- Integration tests in `tests/integration/`
- Updated `pyproject.toml` with CLI entry point

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `python -m nlp2mcp.reporting.generate_report --type=status` works
  - [ ] `python -m nlp2mcp.reporting.generate_report --type=failure` works
  - [ ] `nlp2mcp-report --help` shows usage
  - [ ] GAMSLIB_STATUS.md generated with current metrics (21.3% parse, etc.)
  - [ ] FAILURE_ANALYSIS.md generated with error breakdown
  - [ ] All reporting tests pass (unit + integration)
  - [ ] Quality gate passes (typecheck, lint, format, test)
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
- [ ] **CHECKPOINT 1:** Check off all Checkpoint 1 criteria in PLAN.md:
  - [ ] generate_report.py works
  - [ ] GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md generated

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 3: CLI and Integration [Checkpoint 1]" \
                --body "Completes reporting infrastructure with MarkdownRenderer and generate_report.py CLI. Generates first GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md reports. Completes Checkpoint 1." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 128-161)
- `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` (CLI Design section)
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Unknown 1.3)

---

## Day 4 Prompt: Parse and Translate Gap Analysis

**Branch:** Create a new branch named `sprint16-day4-gap-analysis-parse` from `main`

**Objective:** Deep-dive into parse failures, categorize by root cause, and begin IMPROVEMENT_ROADMAP.md.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 167-197 (Day 4 details)
- Read `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` - Detailed parse error analysis
- Read `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md` - Baseline blockers
- Review generated `docs/testing/FAILURE_ANALYSIS.md` from Day 3
- Review Unknowns 4.1-4.4 in `KNOWN_UNKNOWNS.md` (parse failure analysis)
- Review Unknowns 5.1-5.3 in `KNOWN_UNKNOWNS.md` (translation failure analysis)

**Tasks to Complete (6 hours):**

1. **Generate detailed parse failure report** (1h)
   - Run `generate_report.py --type=failure` with verbose output
   - Cross-reference with `tests/output/pipeline_results.json`
   - List all 126 parse failures with their error categories
   - Identify subcategories within `lexer_invalid_char` (109 models)

2. **Analyze lexer error subcategories** (2h)
   - Using LEXER_ERROR_ANALYSIS.md findings, categorize by root cause:
     - Keyword case issues (e.g., `Free Variable`) - 9 models
     - Hyphenated set elements (e.g., `element-1`) - 3 models
     - Abort statement syntax - 3 models
     - Tuple expansion syntax (e.g., `(a,b).c`) - 12 models
     - Quoted set descriptions - 7 models
     - Other/unclassified
   - Document fix strategy for each subcategory
   - Estimate effort (hours) for each fix
   - Calculate priority score: Models / Effort

3. **Document translation failure patterns** (1h)
   - Analyze 17 translation failures from pipeline_results.json
   - Group by translation error category
   - Document Sprint 17 deferral rationale (per SPRINT_15_REVIEW.md recommendations)
   - Note any translation issues that might be fixed by parse improvements

4. **Begin IMPROVEMENT_ROADMAP.md** (2h)
   - Create `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md`
   - Add header with purpose and methodology
   - Add Priority 1 (High Confidence) improvements:
     | Fix | Models | Effort | Score | Confidence |
     |-----|--------|--------|-------|------------|
     | Keyword case | 9 | 0.5d | 18.0 | High |
     | Hyphenated elements | 3 | 0.5d | 6.0 | High |
     | Abort syntax | 3 | 0.5d | 6.0 | High |
   - Add Priority 2 (Medium Confidence) improvements:
     | Fix | Models | Effort | Score | Confidence |
     |-----|--------|--------|-------|------------|
     | Tuple expansion | 12 | 1.5d | 8.0 | Medium |
     | Quoted descriptions | 7 | 1d | 7.0 | Medium |
   - Add Deferred to Sprint 17 section for translation fixes
   - Reference Unknown 7.1, 7.2 for roadmap format and priority formula

**Deliverables:**
- Detailed parse error analysis (update FAILURE_ANALYSIS.md or separate doc)
- Translation gap analysis documentation
- `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md` (draft with parse improvements)

**Quality Checks:**
This is primarily a documentation day. If any Python files are modified:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Parse failures categorized by subcategory (keyword case, hyphenated, etc.)
  - [ ] Each error category has fix strategy and effort estimate
  - [ ] Translation failures documented with Sprint 17 deferral rationale
  - [ ] IMPROVEMENT_ROADMAP.md draft with top 10 improvements
  - [ ] Priority scores calculated for all improvements
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Document categorization methodology
  - Note any surprises or new findings

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 4: Parse and Translate Gap Analysis" \
                --body "Completes detailed parse failure analysis and creates IMPROVEMENT_ROADMAP.md draft with prioritized fixes." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 167-197)
- `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md`
- `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md`
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Unknowns 4.1-4.4, 5.1-5.3, 7.1-7.2)

---

## Day 5 Prompt: Solve Gap Analysis and Roadmap Finalization

**Branch:** Create a new branch named `sprint16-day5-gap-analysis-solve` from `main`

**Objective:** Analyze solve failures in detail, document emit_gams.py fixes, and finalize IMPROVEMENT_ROADMAP.md.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 199-230 (Day 5 details)
- Read `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md` - Solve failure analysis
- Read Day 4 deliverables: `IMPROVEMENT_ROADMAP.md` draft
- Review Unknowns 6.1-6.2 in `KNOWN_UNKNOWNS.md` (solve failure analysis)
- Review Unknown 8.1-8.4 in `KNOWN_UNKNOWNS.md` (parse blocker targets)
- Review `src/nlp2mcp/ir/emit_gams.py` - Code to fix

**Tasks to Complete (6 hours):**

1. **Analyze solve failure patterns in detail** (1.5h)
   - Cross-reference PATH_ERROR_ANALYSIS.md with pipeline_results.json
   - Document all 14 solve failures (17 translated - 3 success)
   - Group by root cause:
     - Unary minus formatting issues - ~10 models
     - Set element quoting issues - ~3 models
     - Scalar declaration issues - ~1 model
   - Verify 100% are emit_gams.py bugs (per prep task finding)

2. **Document emit_gams.py fix requirements** (1h)
   - For unary minus: Document current `-(expr)` output and required `(-1)*(expr)` format
   - For set element quoting: Document inconsistent quoting patterns
   - For scalar declaration: Document edge case handling needed
   - Identify specific functions in emit_gams.py to modify
   - Note any potential side effects or regression risks

3. **Finalize IMPROVEMENT_ROADMAP.md** (1.5h)
   - Add Solve Improvements section:
     | Fix | Models | Effort | Score | Confidence |
     |-----|--------|--------|-------|------------|
     | Unary minus | 10 | 0.5d | 20.0 | High |
     | Set quoting | 3 | 0.5d | 6.0 | High |
     | Scalar declaration | 1 | 0.25d | 4.0 | High |
   - Add Sprint 16 Implementation Plan section
   - Add Sprint 17 Deferred Work section
   - Add Success Criteria section (from PLAN.md)
   - Finalize priority ordering across all categories

4. **Create implementation task list** (1h)
   - Create detailed tasks for Day 6 (P1 parse fixes):
     - [ ] Fix keyword case in gams.lark (2h)
     - [ ] Fix hyphenated elements in gams.lark (2h)
     - [ ] Fix abort syntax in gams.lark (1h)
     - [ ] Run regression tests (1h)
   - Create detailed tasks for Day 7 (P2 parse fixes):
     - [ ] Add tuple expansion syntax (3h)
     - [ ] Fix quoted descriptions (2h)
     - [ ] Test affected models (1h)
   - Create detailed tasks for Day 8 (solve fixes):
     - [ ] Fix unary minus in emit_gams.py (3h)
     - [ ] Fix set quoting in emit_gams.py (2h)
     - [ ] Fix scalar declaration (0.5h)
     - [ ] Test all translated models (0.5h)

5. **Review dependencies for Phase 3** (1h)
   - Verify gams.lark is understood (review GRAMMAR_EXTENSION_GUIDE.md)
   - Verify emit_gams.py structure is understood
   - Identify test models for each fix
   - Ensure handoff to Day 6 is clear

**Deliverables:**
- Solve error analysis added to FAILURE_ANALYSIS.md or IMPROVEMENT_ROADMAP.md
- Finalized `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md`
- Implementation task list for Days 6-8

**Quality Checks:**
This is primarily a documentation day. If any Python files are modified:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All solve failures mapped to emit_gams.py bugs
  - [ ] IMPROVEMENT_ROADMAP.md complete with priority scores
  - [ ] Implementation tasks defined for each Day 6-8 fix
  - [ ] Clear handoff to improvement phase
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
- [ ] **CHECKPOINT 2:** Check off all Checkpoint 2 criteria in PLAN.md:
  - [ ] IMPROVEMENT_ROADMAP.md finalized
  - [ ] Implementation tasks defined

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 5: Solve Gap Analysis and Roadmap Finalization [Checkpoint 2]" \
                --body "Completes solve failure analysis, finalizes IMPROVEMENT_ROADMAP.md with all priorities, and creates implementation task list for Days 6-8. Completes Checkpoint 2." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 199-230)
- `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md`
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Unknowns 6.1-6.2, 8.1-8.4)
- `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md`

---

## Day 6 Prompt: Parse Improvements - Priority 1 (High Confidence)

**Branch:** Create a new branch named `sprint16-day6-parse-p1` from `main`

**Objective:** Implement low-effort, high-confidence grammar fixes to unblock 15 models.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 236-268 (Day 6 details)
- Read `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md` - Safe grammar patterns
- Read `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` - Specific error patterns
- Read `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md` - Day 6 tasks
- Review Unknown 9.1 in `KNOWN_UNKNOWNS.md` (grammar change approach)
- Review Unknown 9.2 in `KNOWN_UNKNOWNS.md` (testing strategy)
- Review `src/nlp2mcp/parser/gams.lark` - Grammar file to modify

**Tasks to Complete (6 hours):**

1. **Fix keyword case handling** (2h)
   - Issue: GAMS allows `Free Variable`, `POSITIVE VARIABLE`, etc. (case insensitive)
   - Current grammar likely requires lowercase
   - Modify gams.lark to handle mixed case keywords
   - Option A: Use `~"free"i` for case-insensitive matching in Lark
   - Option B: Add explicit alternatives
   - Test with affected models: [list from LEXER_ERROR_ANALYSIS.md]
   - Target: 9 models should now parse

2. **Fix hyphenated set elements** (2h)
   - Issue: Set elements like `element-1`, `us-east-2` fail to parse
   - Current SET_ELEMENT_ID likely doesn't allow hyphens
   - Modify SET_ELEMENT_ID terminal to include hyphen:
     ```
     SET_ELEMENT_ID: /[a-zA-Z][a-zA-Z0-9_-]*/
     ```
   - Be careful not to conflict with minus operator
   - Test with affected models: [list from LEXER_ERROR_ANALYSIS.md]
   - Target: 3 models should now parse

3. **Fix abort statement syntax** (1h)
   - Issue: `abort$(...) 'message'` syntax not recognized
   - Add `abort_stmt` rule to grammar:
     ```
     abort_stmt: "abort" [dollar_condition] [STRING]
     ```
   - Integrate into statement alternatives
   - Test with affected models: [list from LEXER_ERROR_ANALYSIS.md]
   - Target: 3 models should now parse

4. **Run regression tests** (1h)
   - Run full parse test: `python scripts/gamslib/batch_parse.py`
   - Verify all 34 previously-passing models still pass
   - Verify 15 new models now pass (49 total)
   - Document any unexpected failures
   - Run unit tests: `pytest tests/parser/ -v`

**Deliverables:**
- Updated `src/nlp2mcp/parser/gams.lark` with P1 fixes
- All 34 previously-passing models still pass
- 15 newly-passing models documented
- Unit tests for new grammar rules

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

After grammar changes, also run:
```bash
python scripts/gamslib/batch_parse.py --json > /tmp/after_p1.json
# Compare with baseline to ensure no regressions
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Keyword case models (FREE, POSITIVE, NEGATIVE, etc.) now parse
  - [ ] Hyphenated element models now parse
  - [ ] Abort syntax models now parse
  - [ ] No regressions: all 34 existing parses still succeed
  - [ ] Quality gate passes
  - [ ] Parse rate increased from 21.3% to ~30.6% (49/160)
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Update parse rate table with new rate
  - Document each grammar change and models it unlocked

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 6: Parse Improvements - Priority 1" \
                --body "Implements P1 grammar fixes: keyword case, hyphenated elements, abort syntax. Target: +15 models parsing (34→49). No regressions." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 236-268)
- `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md`
- `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md`
- `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md`
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Unknowns 9.1, 9.2)

---

## Day 7 Prompt: Parse Improvements - Priority 2 (Medium Confidence)

**Branch:** Create a new branch named `sprint16-day7-parse-p2` from `main`

**Objective:** Implement medium-effort grammar fixes to unblock 19 additional models.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 270-300 (Day 7 details)
- Read `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md` - Safe grammar patterns
- Read `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` - Tuple and quoted patterns
- Read `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md` - Day 7 tasks
- Review Day 6 results (current parse rate after P1 fixes)
- Verify Day 6 changes merged successfully

**Tasks to Complete (6 hours):**

1. **Add tuple expansion syntax** (3h)
   - Issue: GAMS allows `(a,b).c` to mean `a.c, b.c` (Cartesian product)
   - Current grammar doesn't support parenthesized set tuples in domain expressions
   - Modify domain_expr or set_reference rules:
     ```
     tuple_set: "(" set_ref ("," set_ref)+ ")"
     domain_element: set_ref | tuple_set
     domain_expr: domain_element ("." domain_element)*
     ```
   - This is more complex - may need AST changes too
   - Test with affected models: [list from LEXER_ERROR_ANALYSIS.md]
   - Target: 12 models should now parse

2. **Fix quoted set descriptions** (2h)
   - Issue: Inline descriptions like `i "cities" /a, b, c/` may not parse
   - Current grammar may not handle quoted strings in set definitions correctly
   - Check SET_DEFINITION rule for description placement
   - May need to add optional STRING after set name:
     ```
     set_definition: SET_NAME [STRING] ["/" set_elements "/"]
     ```
   - Test with affected models: [list from LEXER_ERROR_ANALYSIS.md]
   - Target: 7 models should now parse

3. **Test with affected models** (1h)
   - Run parse tests on all 19 target models
   - Verify each model parses without errors
   - Check IR output is reasonable (not just parsing, but correct structure)
   - Document any models that still fail and why
   - Run full regression test to ensure no P1 models broke

**Deliverables:**
- Updated `src/nlp2mcp/parser/gams.lark` with P2 fixes
- 19 newly-passing models documented
- No regressions from Day 6 or Sprint 15 baseline
- Unit tests for new grammar rules

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

After grammar changes, also run:
```bash
python scripts/gamslib/batch_parse.py --json > /tmp/after_p2.json
# Compare with Day 6 baseline to ensure no regressions
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Tuple expansion syntax models now parse
  - [ ] Quoted set description models now parse
  - [ ] No regressions from Day 6 or Sprint 15 baseline
  - [ ] Quality gate passes
  - [ ] Parse rate increased to ~42.5% (68/160) if all P2 models fixed
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Update parse rate table with new rate
  - Document each grammar change and models it unlocked
  - Note any P2 fixes that didn't work as expected

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 7: Parse Improvements - Priority 2" \
                --body "Implements P2 grammar fixes: tuple expansion syntax, quoted set descriptions. Target: +19 models parsing (49→68). No regressions." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 270-300)
- `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md`
- `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md`
- `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md`

---

## Day 8 Prompt: Solve Improvements (emit_gams.py Fixes)

**Branch:** Create a new branch named `sprint16-day8-solve-fixes` from `main`

**Objective:** Fix MCP code generation bugs in emit_gams.py to improve solve rate from 17.6% to 76%+.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 302-336 (Day 8 details)
- Read `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md` - Specific emit_gams.py bugs
- Read `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md` - Day 8 tasks
- Review `src/nlp2mcp/ir/emit_gams.py` - Code to modify
- Review Unknown 8.3, 8.4 in `KNOWN_UNKNOWNS.md` (code generation approach)

**Tasks to Complete (6 hours):**

1. **Fix unary minus formatting** (3h)
   - Issue: `-(expr)` in MCP output causes PATH solver errors
   - Required: `(-1)*(expr)` format for MCP compatibility
   - Locate unary minus handling in emit_gams.py
   - Modify to generate `(-1)*(expr)` instead of `-(expr)`
   - Example: `-x` → `(-1)*x`, `-(a+b)` → `(-1)*(a+b)`
   - Test with affected models (from PATH_ERROR_ANALYSIS.md)
   - Target: ~10 models should now solve

2. **Fix set element quoting** (2h)
   - Issue: Inconsistent quoting of set elements in MCP output
   - Some elements need quotes, some don't, depending on content
   - Review current quoting logic in emit_gams.py
   - Ensure consistent quoting rules:
     - Quote if contains special characters
     - Quote if starts with number
     - Don't quote simple alphanumeric identifiers
   - Test with affected models
   - Target: ~3 models should now solve

3. **Fix scalar declaration edge case** (0.5h)
   - Issue: Scalar without domain may not emit correctly
   - Check scalar handling in emit_gams.py
   - Ensure proper declaration format
   - Test with affected model
   - Target: 1 model should now solve

4. **Test all translated models** (0.5h)
   - Run solve tests on all currently-translated models
   - Run: `python scripts/gamslib/run_full_test.py --only-translated`
   - Verify hs62 (golden test) still solves and matches
   - Count newly-solving models
   - Document any remaining solve failures

**Deliverables:**
- Updated `src/nlp2mcp/ir/emit_gams.py` with solve fixes
- Solve results for all translated models
- Updated solve metrics
- No regressions (hs62 still works)

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

After emit_gams.py changes, also run:
```bash
python scripts/gamslib/run_full_test.py --only-translated --verbose
# Verify solve improvements
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Unary minus models now solve correctly
  - [ ] Quoting issue models now solve correctly
  - [ ] Scalar declaration model now solves
  - [ ] No regressions: hs62 still solves and matches
  - [ ] Quality gate passes
  - [ ] Solve rate increased from 17.6% to 60%+ (minimum target)
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Update solve rate with new metrics
  - Document each emit_gams.py fix
- [ ] **CHECKPOINT 3:** Check off all Checkpoint 3 criteria in PLAN.md:
  - [ ] Grammar and emit_gams.py fixes implemented
  - [ ] No regressions

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 8: Solve Improvements [Checkpoint 3]" \
                --body "Fixes emit_gams.py bugs: unary minus formatting, set element quoting, scalar declaration. Target: solve rate 17.6%→60%+. Completes Checkpoint 3." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 302-336)
- `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md`
- `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md`
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` (Unknowns 8.3, 8.4)

---

## Day 9 Prompt: Full Pipeline Retest

**Branch:** Create a new branch named `sprint16-day9-retest` from `main`

**Objective:** Run complete pipeline on all 160 models, measure improvements, create Sprint 16 baseline snapshot.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 342-372 (Day 9 details)
- Verify Days 6-8 changes all merged successfully
- Review current baseline_metrics.json (Sprint 15 baseline)
- Review `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - Progress tracking schema

**Tasks to Complete (5 hours):**

1. **Run full pipeline on all 160 models** (1h)
   - Run: `python scripts/gamslib/run_full_test.py --all --verbose`
   - Capture full output to log file
   - Monitor for any errors or crashes
   - Expect runtime: ~30-60 minutes for full pipeline

2. **Generate Sprint 15 vs Sprint 16 comparison** (1h)
   - Run: `python -m nlp2mcp.reporting.generate_report --type=all`
   - Review generated GAMSLIB_STATUS.md for new metrics
   - Review generated FAILURE_ANALYSIS.md for updated error breakdown
   - Use ProgressAnalyzer to compute deltas:
     - Parse rate delta: 21.3% → X% (target: ≥31.3%)
     - Solve rate delta: 17.6% → X% (target: ≥60%)
     - Full pipeline delta: 0.6% → X% (target: ≥3%)

3. **Analyze unexpected results** (2h)
   - Identify any regressions (models that passed before, fail now)
   - Investigate root causes of regressions
   - Fix any regressions found (may require additional commits)
   - Document any models that should have improved but didn't
   - Note any surprising successes (models not targeted that now work)

4. **Create new baseline snapshot** (1h)
   - Update `tests/output/baseline_metrics.json` with Sprint 16 metrics
   - Update `tests/output/pipeline_results.json` with new results
   - Create progress history entry (if progress_history.json exists):
     ```json
     {
       "snapshot_id": "sprint16_20260130",
       "timestamp": "2026-01-30T...",
       "metrics": { ... }
     }
     ```
   - Verify all files are valid JSON

**Deliverables:**
- Updated `tests/output/pipeline_results.json`
- Updated `tests/output/baseline_metrics.json`
- Sprint comparison report (in SPRINT_LOG.md)
- New snapshot in progress tracking (if applicable)

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Full pipeline run complete without errors
  - [ ] New metrics captured in baseline_metrics.json
  - [ ] Comparison report shows improvement delta
  - [ ] Any regressions identified and fixed
  - [ ] Parse rate meets minimum target (≥31.3%)
  - [ ] Solve rate meets minimum target (≥60%)
  - [ ] Full pipeline rate meets minimum target (≥3%)
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
  - Complete metrics comparison table
  - Document any regressions and fixes
  - Note final parse/solve/pipeline rates

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 9: Full Pipeline Retest" \
                --body "Completes full pipeline retest on all 160 models. Updates baseline metrics. Parse: 21.3%→X%, Solve: 17.6%→X%, Pipeline: 0.6%→X%." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 342-372)
- `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` (Progress Tracking section)
- `tests/output/baseline_metrics.json` (Sprint 15 baseline)

---

## Day 10 Prompt: Documentation and Retrospective

**Branch:** Create a new branch named `sprint16-day10-retrospective` from `main`

**Objective:** Finalize all documentation, write sprint retrospective, and plan Sprint 17 prep tasks.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_16/PLAN.md` lines 374-408 (Day 10 details)
- Review Day 9 results (final metrics)
- Review `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md` - Sprint progress
- Review `docs/planning/EPIC_3/SPRINT_15/SPRINT_15_REVIEW.md` - Format reference

**Tasks to Complete (5 hours):**

1. **Update GAMSLIB_STATUS.md** (1h)
   - Regenerate with final metrics: `python -m nlp2mcp.reporting.generate_report --type=status`
   - Review for accuracy
   - Ensure all metrics reflect Sprint 16 final state
   - Add any manual annotations needed

2. **Update SPRINT_BASELINE.md** (1h)
   - Update `docs/testing/SPRINT_BASELINE.md` with Sprint 16 baseline
   - Include:
     - Final parse/translate/solve/pipeline rates
     - Model counts per stage
     - Error category breakdown
     - Comparison with Sprint 15
     - Key improvements made

3. **Write Sprint 16 retrospective** (1.5h)
   - Create `docs/planning/EPIC_3/SPRINT_16/SPRINT_RETROSPECTIVE.md`
   - Structure:
     - **Summary:** Goals achieved, metrics improved
     - **What Worked Well:** Successful approaches, good decisions
     - **What Could Be Improved:** Challenges, lessons learned
     - **Key Technical Decisions:** Grammar changes, emit_gams.py fixes
     - **Metrics Achieved vs Targets:**
       | Metric | Target | Achieved | Status |
       |--------|--------|----------|--------|
       | Parse Rate | ≥31.3% | X% | ✅/❌ |
       | Solve Rate | ≥60% | X% | ✅/❌ |
       | Pipeline | ≥3% | X% | ✅/❌ |
     - **Recommendations for Sprint 17**

4. **Plan Sprint 17 prep tasks** (1h)
   - Identify Sprint 17 priorities based on:
     - Remaining parse failures (from FAILURE_ANALYSIS.md)
     - Translation improvements (deferred from Sprint 16)
     - Any regressions or issues discovered
   - Draft Sprint 17 prep task outline:
     - Task 1: Create Known Unknowns
     - Task 2: Analyze remaining parse blockers
     - Task 3: Research translation improvements
     - etc.
   - Document in SPRINT_RETROSPECTIVE.md or separate file

5. **Final commit and review** (0.5h)
   - Review all Sprint 16 deliverables complete
   - Verify all acceptance criteria met
   - Ensure PLAN.md has all days marked complete
   - Final quality checks

**Deliverables:**
- Updated `docs/testing/GAMSLIB_STATUS.md`
- Updated `docs/testing/SPRINT_BASELINE.md`
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_RETROSPECTIVE.md`
- Sprint 17 prep task outline

**Quality Checks:**
This is primarily a documentation day. If any Python files are modified:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] GAMSLIB_STATUS.md reflects Sprint 16 final metrics
  - [ ] SPRINT_BASELINE.md updated with Sprint 16 baseline
  - [ ] Retrospective documents successes and improvements
  - [ ] Sprint 17 priorities identified
  - [ ] All Sprint 16 code committed and tested
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_3/SPRINT_16/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log final entry to `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`
- [ ] **CHECKPOINT 4:** Check off all Checkpoint 4 criteria in PLAN.md:
  - [ ] Full retest done
  - [ ] Documentation updated
  - [ ] Retrospective written
- [ ] **SPRINT COMPLETE:** All deliverables done, all checkpoints passed

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 16 Day 10: Documentation and Retrospective [SPRINT COMPLETE]" \
                --body "Finalizes Sprint 16 documentation, writes retrospective, and plans Sprint 17. All checkpoints complete. Sprint 16 DONE." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_16/PLAN.md` (lines 374-408)
- `docs/planning/EPIC_3/SPRINT_15/SPRINT_15_REVIEW.md` (format reference)
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_LOG.md`

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Create the specified branch from `main`
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant change
   - Track progress against time estimates
   - Commit incrementally for complex changes

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update PLAN.md, CHANGELOG.md
   - Update SPRINT_LOG.md with PR entry
   - Create PR and request Copilot review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

5. **SPRINT_LOG.md updates:**
   - Update after each PR merge with PR entry
   - Update parse rate table when parse rate changes
   - Document key decisions immediately while context is fresh
   - Complete final metrics tables on Day 10
   - See `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` for templates

---

## Notes

- Each prompt is designed to be self-contained with all necessary context
- Prerequisites ensure you have necessary background before starting
- Quality checks ensure code quality throughout the sprint
- Completion criteria provide clear definition of "done" for each day
- All prompts reference specific line numbers in PLAN.md for detailed task descriptions
- PR & Review workflow ensures thorough code review before merging
- Checkpoints (Days 3, 5, 8, 10) provide sprint progress validation
- Success criteria from PLAN.md:
  - Minimum: Parse ≥31.3%, Solve ≥60%, Pipeline ≥3%
  - Target: Parse ≥37.5%, Solve ≥76%, Pipeline ≥5%
  - Stretch: Parse ≥49.4%, Solve 100%, Pipeline ≥8%

---

*Document created: January 20, 2026*  
*Sprint 16 Duration: Days 0-10 (11 working days including setup)*

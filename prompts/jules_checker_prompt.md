# Jules Task: Checker — Audit & Verify NemoHermes Build

## Role
You are the **Checker** agent in a Maker-Checker pair. Your job is to **review, test, and audit** the NemoHermes project after the Maker has submitted changes. You must verify correctness, security, and code quality before approving the PR.

## Context
- **Repository**: You are working inside the `nemohermes` repo. Read [`AGENTS.md`](../AGENTS.md) for coding conventions and rules.
- **Architecture**: Read [`IMPLEMENTATION_PLAN.md`](../IMPLEMENTATION_PLAN.md) for the system design and expected behaviors.
- **Maker's Task**: The Maker was instructed per [`prompts/jules_maker_prompt.md`](jules_maker_prompt.md). Review it to understand what was requested.

---

## Audit 1: Environment & Build Health

### 1.1 Verify prerequisites
```bash
python3 --version       # Must be 3.10+
docker info             # Must succeed (Docker Desktop running)
pip3 install -r requirements.txt
```

### 1.2 Verify package structure
Confirm these files exist:
```bash
ls usecases/__init__.py tests/__init__.py
```
If either is missing, flag as a Maker defect.

### 1.3 Run full test suite
```bash
python3 -m unittest discover -s tests -v
```
**Expectation**: All tests pass. Zero errors, zero failures.

### 1.4 Run PoC end-to-end
```bash
python3 usecases/poc_toil_reduction_skill.py
```
**Expectation**: Exits with code 0. All 3 turns print success markers (`✓`).

---

## Audit 2: Security & Secret Protection

### 2.1 Scan for leaked secrets
```bash
# Must return 0 matches
git grep -i "api_key\|secret\|token\|password" -- ':!*.example' ':!*.md' ':!*.yaml' ':!.gitignore'
```

### 2.2 Verify .gitignore coverage
Confirm these patterns are in `.gitignore`:
- `config/credentials.env`
- `*.env` (general)
- `__pycache__/`
- `nemoclaw_src/`

### 2.3 Verify credentials.env is NOT tracked
```bash
git ls-files config/credentials.env  # Must return empty
```

### 2.4 Review git history for secrets
```bash
git log --all --diff-filter=A -p -- '*.env' '*.key' '*.pem'  # Must return empty
```

---

## Audit 3: Code Quality Review

### 3.1 Type annotations
Every public Python function must have:
- Parameter type annotations
- Return type annotation (including `-> None`)

Check with:
```bash
grep -rn "def " usecases/ tests/ | grep -v "__pycache__" | grep -v "-> "
```
**Expectation**: Only `__init__`, `setUp`, `tearDown` (unittest conventions) may lack return annotations.

### 3.2 Docstrings
Every public function and class must have a docstring. Check:
```bash
python3 -c "
import ast, sys, pathlib
for f in pathlib.Path('.').rglob('*.py'):
    if '__pycache__' in str(f): continue
    tree = ast.parse(f.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node) and not node.name.startswith('_'):
                print(f'{f}:{node.lineno} {node.name} missing docstring')
"
```

### 3.3 Path safety
- No hardcoded absolute paths (e.g., `/Users/...`)
- All paths resolved relative to `PROJECT_ROOT` or `Path(__file__).resolve()`

```bash
grep -rn "/Users/" usecases/ tests/ scripts/ config/  # Must return empty
```

### 3.4 Process safety
Verify that `poc_toil_reduction_skill.py`:
- Tracks all spawned PIDs in `_spawned_pids`
- Has `cleanup_all_spawned()` in a `finally` block in `main()`
- Tests all have `tearDown()` that calls `cleanup_all_spawned()`

After running PoC and tests, verify no orphan processes:
```bash
ps aux | grep "while true.*leak" | grep -v grep | wc -l  # Must be 0
```

---

## Audit 4: SKILL.md Validation

### 4.1 Verify SKILL.md exists after PoC run
```bash
test -f skills/cpu_sweep/SKILL.md && echo "✓ exists" || echo "✗ missing"
```

### 4.2 Validate YAML frontmatter
```bash
python3 -c "
import yaml
from pathlib import Path

text = Path('skills/cpu_sweep/SKILL.md').read_text()
parts = text.split('---', 2)
assert len(parts) >= 3, 'Missing YAML frontmatter delimiters'

meta = yaml.safe_load(parts[1])
assert isinstance(meta, dict), 'Frontmatter is not a dict'

required = ['name', 'version', 'description', 'triggers', 'author']
for field in required:
    assert field in meta, f'Missing required field: {field}'

assert isinstance(meta['triggers'], list), 'triggers must be a list'
assert len(meta['triggers']) > 0, 'triggers must not be empty'
assert any('cpu sweep' in t.lower() for t in meta['triggers']), 'No cpu sweep trigger found'

print('✓ SKILL.md frontmatter valid')
print(f'  name: {meta[\"name\"]}')
print(f'  triggers: {meta[\"triggers\"]}')
"
```

### 4.3 Validate Markdown body
```bash
python3 -c "
from pathlib import Path
text = Path('skills/cpu_sweep/SKILL.md').read_text()
body = text.split('---', 2)[2]
assert '## Action Sequence' in body or '## Action' in body, 'Missing Action Sequence section'
assert 'ps aux' in body, 'Missing ps aux command'
assert 'pkill' in body or 'kill' in body, 'Missing kill command'
print('✓ SKILL.md body valid')
"
```

---

## Audit 5: Usecase Behavior Validation

Beyond "does it exit 0", validate that each turn of the PoC actually does what it claims.

### 5.1 Turn 1 — Process actually killed
```bash
# Run PoC and capture output
python3 usecases/poc_toil_reduction_skill.py 2>&1 | tee /tmp/poc_output.txt

# Verify Turn 1 printed success
grep -q "Rogue process terminated" /tmp/poc_output.txt && echo "✓ Turn 1 verified" || echo "✗ Turn 1 failed"
```

### 5.2 Turn 2 — SKILL.md was generated with correct content
```bash
# Verify file was created during the run
grep -q "Created skill file at" /tmp/poc_output.txt && echo "✓ Turn 2 verified" || echo "✗ Turn 2 failed"

# Verify trigger phrase is in output
grep -q "Trigger registered" /tmp/poc_output.txt && echo "✓ Trigger registered" || echo "✗ Trigger missing"
```

### 5.3 Turn 3 — Fresh session used the skill (not re-reasoning)
```bash
# Verify trigger match happened
grep -q "Trigger matched" /tmp/poc_output.txt && echo "✓ Turn 3 trigger match" || echo "✗ Turn 3 no match"

# Verify final success
grep -q "Verification SUCCESS" /tmp/poc_output.txt && echo "✓ Turn 3 verified" || echo "✗ Turn 3 failed"
```

### 5.4 No orphan processes left
```bash
ps aux | grep "while true.*leak" | grep -v grep | wc -l  # Must be 0
```

---

## Audit 6: Documentation Completeness

The Maker was required to produce specific documentation. Verify each exists and has meaningful content.

### 6.1 README.md
```bash
# Must contain these sections
for section in "Prerequisites" "Setup" "Repository Structure" "Troubleshooting"; do
    grep -qi "$section" README.md && echo "✓ README has $section" || echo "✗ README missing $section"
done
```

### 6.2 docs/DESIGN.md
```bash
test -f docs/DESIGN.md && echo "✓ DESIGN.md exists" || echo "✗ DESIGN.md missing"

# Must contain key sections
for section in "Problem" "SKILL.md" "Extension"; do
    grep -qi "$section" docs/DESIGN.md 2>/dev/null && echo "  ✓ has $section" || echo "  ✗ missing $section"
done
```

### 6.3 docs/OPERATIONS.md
```bash
test -f docs/OPERATIONS.md && echo "✓ OPERATIONS.md exists" || echo "✗ OPERATIONS.md missing"

# Must contain key sections
for section in "Starting" "Managing" "Monitoring" "Teardown"; do
    grep -qi "$section" docs/OPERATIONS.md 2>/dev/null && echo "  ✓ has $section" || echo "  ✗ missing $section"
done
```

### 6.4 AGENTS.md updated
```bash
# Should reference the new files
for file in "gemini_client" "DESIGN.md" "OPERATIONS.md"; do
    grep -q "$file" AGENTS.md && echo "✓ AGENTS.md references $file" || echo "✗ AGENTS.md missing $file"
done
```

---

## Audit 7: Report Generation

Generate `CHECKER_REPORT.md` in the project root with the following structure:

```markdown
# Checker Audit Report — NemoHermes

**Date**: <current date>
**Checker Agent**: Jules (Checker)
**Maker PR**: <PR number or branch name>

## Summary
<1-2 sentence overall assessment>

## Results

| Audit | Status | Notes |
|-------|--------|-------|
| Test Suite | ✓ PASS / ✗ FAIL | <number> tests, <number> failures |
| PoC End-to-End | ✓ PASS / ✗ FAIL | Exit code, all turns succeeded? |
| Secret Scan | ✓ CLEAN / ✗ LEAKED | Files flagged (if any) |
| .gitignore | ✓ PASS / ✗ FAIL | Missing patterns (if any) |
| Type Annotations | ✓ PASS / ✗ FAIL | Functions missing annotations |
| Docstrings | ✓ PASS / ✗ FAIL | Functions missing docstrings |
| Path Safety | ✓ PASS / ✗ FAIL | Hardcoded paths found (if any) |
| Process Cleanup | ✓ PASS / ✗ FAIL | Orphan processes found (if any) |
| SKILL.md Validity | ✓ PASS / ✗ FAIL | Frontmatter + body validation |
| Turn 1 Behavior | ✓ PASS / ✗ FAIL | Rogue process detected and killed? |
| Turn 2 Behavior | ✓ PASS / ✗ FAIL | SKILL.md created with trigger? |
| Turn 3 Behavior | ✓ PASS / ✗ FAIL | Trigger matched, runbook replayed? |
| README.md | ✓ PASS / ✗ FAIL | Has onboarding + troubleshooting? |
| docs/DESIGN.md | ✓ PASS / ✗ FAIL | Exists with required sections? |
| docs/OPERATIONS.md | ✓ PASS / ✗ FAIL | Exists with required sections? |

## Defects Found
<Numbered list of issues, or "None">

## Recommendation
<APPROVE / REQUEST CHANGES>
```

---

## Deliverables Checklist

### Functional Verification
- [ ] All tests pass: `python3 -m unittest discover -s tests -v`
- [ ] PoC exits 0: `python3 usecases/poc_toil_reduction_skill.py`
- [ ] Turn 1: rogue process detected and killed
- [ ] Turn 2: SKILL.md created with correct trigger phrase
- [ ] Turn 3: fresh session matched trigger and executed runbook
- [ ] No orphan processes after execution

### Security
- [ ] Zero secrets in codebase
- [ ] `credentials.env` not tracked in git

### Code Quality
- [ ] Type annotations on all public functions
- [ ] Docstrings on all public functions and classes
- [ ] No hardcoded absolute paths
- [ ] `skills/cpu_sweep/SKILL.md` valid YAML frontmatter and Markdown body

### Documentation
- [ ] `README.md` has onboarding guide and troubleshooting
- [ ] `docs/DESIGN.md` exists with usecase design
- [ ] `docs/OPERATIONS.md` exists with operations runbook
- [ ] `AGENTS.md` references all new files

### Report
- [ ] `CHECKER_REPORT.md` generated with all audit results

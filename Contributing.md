# Contributing to Netra

Thank you for your interest in improving Netra. This guide explains how to set up the project, how the code is organized, and how to submit changes.

By taking part, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Ways to Contribute

- Report bugs
- Suggest features
- Improve documentation
- Add tests
- Fix issues or build roadmap items from the [README](README.md)

For security problems, **do not open a public issue**. Follow [SECURITY.md](SECURITY.md) instead.

---

## Getting Set Up

1. **Fork** the repository and clone your fork.
2. Follow the setup steps in the [README](README.md): create a virtual environment, install the backend packages, set up PostgreSQL, and install the frontend packages.
3. Create a branch for your work:

   ```bash
   git checkout -b feature/short-description
   ```

Branch name prefixes:

| Prefix | Use for |
| --- | --- |
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `refactor/` | Code cleanup without behavior change |
| `test/` | Adding or improving tests |

---

## How the Code Is Organized

Please keep to these design rules. They make Netra easier to test and extend.

1. **Detection modules stay independent.** Files in `backend/detection/` should not import each other. `pipeline.py` is the only file that connects them, by passing data between them.
2. **API files stay thin.** Files in `backend/api/` receive requests, call other code, and return results. Detection logic does not belong there.
3. **One job per file.** For example, `vehicle_tracker.py` stores position history. It does not assign IDs or apply rules.
4. **Settings live in `config.py`.** Do not scatter thresholds and paths as magic numbers through the code.
5. **Load the model once.** Never load YOLO per frame or per request.
6. **Store file paths, not files, in the database.**

### Adding a new detection rule

1. Write the rule as a function in the matching file (or a new file in `detection/`). It should take plain data in and return an event or `None`.
2. Add any thresholds to `config.py`.
3. Call the rule from `pipeline.py`.
4. Make sure alerts are de-duplicated (use the existing alert key and cooldown approach).
5. Add tests using fake vehicle data. You should not need to run YOLO to test a rule.
6. Update the README features list and the CHANGELOG.

---

## Code Style

**Python**

- Follow PEP 8.
- Use type hints on function signatures.
- Use clear names (`wrong_way_counter`, not `wc`).
- Add short comments that explain *why*, not what the line obviously does.
- Suggested tools: `ruff` or `flake8` for linting and `black` for formatting.

**JavaScript / React**

- Use functional components and hooks.
- Keep components small and reusable.
- Put API and WebSocket calls in `services/`, not inside components.
- Suggested tools: ESLint and Prettier.

---

## Testing

- Test new logic before opening a pull request.
- For detection rules, prefer small unit tests with fake inputs, such as a hand-written list of vehicles and positions.
- When changing detection behavior, test on a few different videos (day, night, different camera angles) and mention the results in your pull request.
- Do not commit real traffic footage. It can contain faces and license plates. Use public sample videos or synthetic clips, and link to them instead of adding the files.
- Do not commit large model files or processed videos. Keep them out of Git using `.gitignore`.

---

## Commit Messages

Use short, clear messages in the present tense, with an optional prefix:

```
feat: add wrong-way confirmation counter
fix: handle vehicles with fewer than two history points
docs: explain ByteTrack settings in README
refactor: move lane polygons into config
test: add counting line crossing cases
```

Keep each commit focused on one change.

---

## Pull Requests

Before opening a pull request, check that:

- [ ] The branch is up to date with `main`
- [ ] The code runs and tests pass
- [ ] New logic has tests
- [ ] No secrets, `.env` files, videos, or model files are included
- [ ] Documentation is updated if behavior changed
- [ ] `CHANGELOG.md` has an entry under **Unreleased**
- [ ] The pull request is focused on one thing

In the description, explain:

1. **What** changed
2. **Why** it changed
3. **How** you tested it
4. Screenshots or short clips (non-sensitive) for dashboard or detection changes

A maintainer will review your pull request. Please be open to feedback, and expect a few rounds of changes on larger contributions.

---

## Reporting Bugs

Open an issue with:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Your operating system, Python version, and whether you use a GPU
- Relevant logs or error messages (remove any private data)

## Suggesting Features

Open an issue describing the problem you want to solve, not only the solution. Mention which roadmap step it relates to if you can.

---

## Licensing of Contributions

By submitting a contribution, you agree that it may be distributed under the project's license. Also note that Netra uses Ultralytics YOLO, which is available under AGPL-3.0 or an Enterprise license. Keep that in mind when adding code that interacts with it.

---

Thank you for helping build Netra.
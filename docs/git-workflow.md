# Git workflow

The repository uses `main` as the stable integration branch. No feature work should be committed directly to it.

## Branches

Create a focused branch from the latest main:

```bash
git switch main
git pull
git switch -c feature/<feature-name>
```

Planned branches include:

- `feature/calendar`
- `feature/timeline`
- `feature/user-dashboard`
- `feature/git-integration`
- `feature/project-runner`

## Synchronization strategy

This project uses `git merge main` as the default way to bring current main into a feature branch:

```bash
git switch feature/<feature-name>
git merge main
```

Do not randomly mix merge and rebase across the team. If the team later chooses rebase, make that an explicit shared policy and update this document.

## Conflicts and Pull Requests

Resolve conflicts on the feature branch, understand both sides, and run `./scripts/test.sh` before opening a Pull Request. Never blindly choose `ours` or `theirs`. Open a Pull Request into `main` for review; merge only after the application, tests, migrations, and documentation checks pass.

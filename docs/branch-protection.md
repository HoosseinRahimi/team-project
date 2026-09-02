# Recommended branch protection for `main`

Configure in GitHub: **Settings → Branches → Add branch protection rule** for
`main`. Recommended settings for this team:

| Setting | Value |
| --- | --- |
| Require a pull request before merging | ✅ enabled |
| Required approvals | 1 (lightweight peer review) |
| Require status checks to pass | ✅ enabled |
| Required status checks | `conflict-marker-check`, `backend`, `frontend` |
| Require branches to be up to date before merging | ✅ enabled |
| Do not allow force pushes | ✅ enabled |
| Do not allow deletions | ✅ enabled |
| Allow squash merging | ✅ enabled (default) |
| Allow merge commits / rebase merging | ❌ disabled (keep history uniform) |

The repository owner should apply these after the first push. Do not add
enterprise-style approval bureaucracy beyond one review.

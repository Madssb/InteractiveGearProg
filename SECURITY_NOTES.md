# Security Notes

## NPM audit status (frontend)

As of 2026-02-23, `npm audit` in `frontend/` reports remaining high-severity findings from `minimatch` through ESLint internals:

- `eslint` -> `@eslint/config-array` / `@eslint/eslintrc` -> `minimatch`

### Why this is deferred

- This path is in `devDependencies` (lint tooling), not shipped browser runtime code.
- `npm audit fix` resolved non-breaking issues.
- Full removal currently requires a breaking upgrade path (`eslint@10`).
- For now, this is accepted as short-term dev-tooling risk while prioritizing feature work.

### Re-check commands

Run from `frontend/`:

```bash
nvm use
npm audit
npm audit --omit=dev
```

### Future cleanup plan

When ready for tooling upgrades:

1. Upgrade ESLint major and compatible plugins.
2. Fix resulting config/rule breakages.
3. Re-run `npm run lint`, `npm run build`, and `npm audit`.

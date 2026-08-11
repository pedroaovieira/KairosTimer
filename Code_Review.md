## Code Review: Kairos Timer (KairosTimer)

### Summary
Clean, single-purpose Android app — solid MVVM separation (ViewModel/Repository/Adapter) and no risky runtime behavior. The one critical issue is hardcoded signing credentials committed to git; the rest are maintainability and minor correctness items.

### Critical Issues

| # | File | Line | Issue | Severity |
|---|------|------|-------|----------|
| 1 | app/build.gradle | 19–24 | Keystore `storePassword`/`keyPassword` hardcoded as `"KairosTimer2024"` and committed (commit `99b7eb1`). The `.jks` is gitignored, but the password — the actual secret — is in history. Anyone with repo read access has it. | 🔴 Critical |

For #1: move the passwords out of `build.gradle` into `gradle.properties` (which is in `.gitignore`) or environment variables, and read them via `project.findProperty("KEYSTORE_PASSWORD")`. Then purge them from history (`git filter-repo`) and rotate. Since you publish to Play, enabling **Play App Signing** is the cleanest long-term fix — Google holds the signing key and you only manage a resettable upload key.

### Suggestions

| # | File | Line | Suggestion | Category |
|---|------|------|------------|----------|
| 2 | repo root | — | `PresentationTimer.apk` (6 MB) is committed. Binaries bloat history and risk shipping stale/signed artifacts. Remove, gitignore `*.apk`, attach builds to GitHub Releases instead. | Maintainability |
| 3 | AndroidManifest.xml | 5 | `allowBackup="true"` lets `adb backup` extract the phases SharedPreferences. Low impact (no sensitive data) — set `false` or add `dataExtractionRules` to be explicit. | Security |
| 4 | PhaseAdapter.kt | 61, 70, 77, 87, 115 | `pos != RecyclerView.NO_ID.toInt()` is the wrong sentinel — the correct guard for an adapter position is `RecyclerView.NO_POSITION`. Both equal -1, so it works by accident; switch for correctness/clarity. | Correctness |
| 5 | MainActivity.kt | 127, 129 | `String.format("%02d…")` without a `Locale` triggers lint and renders non-Latin digits in some locales. Use `String.format(Locale.US, …)`. | Correctness |
| 6 | MainActivity.kt | 31–35, 178–189 | Many color hex strings (`#5AF0B3`, `#1A1A1A`, …) hardcoded in code. Move to `colors.xml` so theme/design stays in one place. | Maintainability |
| 7 | MainActivity.kt | 219–222, 239, 245 | UI strings (`"INITIALIZE"`, `"READY"`, `"PAUSE"`) are hardcoded. `supportsRtl` is on, but hardcoded strings block localization — move to `strings.xml`. | Maintainability |
| 8 | app/build.gradle | 34 | `minifyEnabled false` for release — no shrinking/obfuscation. Enabling R8 reduces size and adds light hardening. | Performance |
| 9 | (whole project) | — | No tests. `TimerViewModel.computePhase` and the H/M/S→millis math are pure logic, ideal for fast unit tests. | Testing |
| 10 | PhaseAdapter.kt | 92–123 | `setupColorSwatches` rebuilds all 12 swatch views on every tap. Fine at this scale, but toggling stroke on the affected two views would be cleaner. | Performance |

### What Looks Good
Clear MVVM boundaries and lifecycle handling — timers cancelled in `onCleared`/`onDestroy`, animators torn down properly. `PhasesRepository` wraps JSON parsing in try/catch with a sensible default fallback. Activities correctly scoped with `exported` (only `MainActivity` is exported, as it must be). No network, no dynamic intents, no injection surface.

### Verdict
**Request Changes** — only because of finding #1. Rotate the signing credentials and get them out of version control; everything else is safe to address incrementally.

---

### Fixes Applied

The following issues were fixed immediately:

- **#1 (Critical) — Signing credentials**: `app/build.gradle` no longer contains passwords. Credentials are now loaded from a gitignored `keystore.properties` file (with env-var fallback for CI). A committed `keystore.properties.template` documents the expected format for collaborators.
- **#2 — APK**: `*.apk` added to `.gitignore`.
- **#5 — Locale**: `MainActivity` timer formatters now use `Locale.US`.

### Remaining Action Items

1. **Purge password from git history** — `KairosTimer2024` is still in commit `99b7eb1`. Run `git filter-repo` (or BFG) to scrub it, then force-push. Treat the password as compromised until rotated.
2. **Untrack the committed APK** — `.gitignore` prevents future commits but doesn't remove an already-tracked file. Run:
   ```
   git rm --cached PresentationTimer.apk
   ```
3. **Consider Play App Signing** — Google holds the real signing key; a leaked upload key can be reset from the Play Console. This is the durable fix for #1.
4. Address suggestions #3–10 incrementally as time allows.

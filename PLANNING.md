# PresentationTimer — Planning

Future features and development ideas.

---

## Backlog

### JSON Presentation Import

Allow the user to import a JSON file that defines a phase per slide, each with its own duration and colour. The timer would advance automatically through phases as the presenter moves through slides — no manual configuration needed.

**Proposed JSON format**

```json
{
  "title": "My Conference Talk",
  "slides": [
    { "slide": 1, "title": "Introduction",   "duration_seconds": 120, "color": "#5AF0B3", "message": "Introduction" },
    { "slide": 2, "title": "Problem",        "duration_seconds": 180, "color": "#5AF0B3", "message": "Problem statement" },
    { "slide": 3, "title": "Solution",       "duration_seconds": 240, "color": "#FFB95F", "message": "Solution" },
    { "slide": 4, "title": "Demo",           "duration_seconds": 300, "color": "#FFB95F", "message": "Live demo" },
    { "slide": 5, "title": "Conclusion",     "duration_seconds": 60,  "color": "#FFCAC5", "message": "Wrap up!" }
  ]
}
```

**Behaviour**
- Total timer duration = sum of all `duration_seconds`
- Each slide maps to a phase; the app tracks which slide is active based on elapsed time
- A **"Next slide"** tap advances to the next phase instantly (the remaining time for the current slide is discarded or carried over — TBD)
- The colour and message for each slide come from the JSON, not from the global phase thresholds
- A slide indicator (e.g. "Slide 3 / 5") is shown on screen

**Implementation notes**
- Add an **Import** button on the setup screen (next to the gear icon)
- Use Android's `ActivityResultContracts.GetContent` with `application/json` MIME type to open the file picker
- Parse with `org.json` (already available) or `kotlinx.serialization`
- Validate: every slide must have `duration_seconds > 0` and a valid hex colour
- Store the imported plan separately from the manually configured phases (do not overwrite user's phases)
- Show a preview of the imported plan before starting (slide count, total duration)

---

### ✅ Visual Polish — Screenshot-Driven Iteration *(completed 2026-04-19)*

The mock screenshots look great but the real app doesn't match them closely enough. Use Claude's vision capability to close the gap iteratively.

**Approach**
- Build a debug APK and run it on a device or emulator
- Take a screenshot of the actual app (each key state: setup, running, paused, finished, settings)
- Share the screenshot with Claude alongside the target mock from `docs/screenshots/`
- Claude identifies the differences (spacing, font sizes, colours, layout) and proposes code changes
- Rebuild, screenshot again, repeat until the real app matches the mock

**States to check**
- Setup screen: headline size, input card proportions, preset pills alignment
- Running screen: timer digit size, halo glow visibility, progress row, segmented pill sizing and spacing
- Paused screen: faded digit opacity, RESUME label
- Finished screen: flash animation, RESET button placement
- Settings screen: slider track and thumb styling, swatch size and spacing, card padding

**Implementation notes**
- Use `adb exec-out screencap -p > screen.png` to capture the device screen without needing a UI tool
- Compare real vs mock side-by-side; the mock is the design target
- Focus changes on `activity_main.xml` (dimensions, margins) and `MainActivity.kt` (animator params) before touching colours
- After each round, regenerate the mock screenshot if the design decision changes so they stay in sync

---

### ✅ Fix About Screen — Version and Year *(completed 2026-04-19)*

The About screen hardcodes both the app version string and the copyright year. Both are currently wrong.

- **Version:** shown as `1.3.2` — should reflect the current release (`1.4.0`) and ideally be sourced from `BuildConfig.VERSION_NAME` so it never drifts again
- **Year:** copyright shows `© 2025` — should be `© 2026`

**Implementation notes**
- In `AboutActivity`, replace the hardcoded version `TextView` with `BuildConfig.VERSION_NAME`
- Update copyright string to `© 2026 Pedro Vieira` (or make it dynamic with `Calendar.getInstance().get(Calendar.YEAR)`)
- Update the version in `docs/make_screenshots.py` (`screen_about`) to match

---

### App Name

The current name "PresentationTimer" is functional but generic. "TEMPORAL" (the in-app brand shown on screen) is already more distinctive and memorable — worth considering as the official name.

**Questions to settle**
- Should the app name match the on-screen brand (`TEMPORAL`) for consistency?
- Is "TEMPORAL" too abstract for discoverability on the Play Store?
- Alternative directions: a name that evokes the presenter experience rather than the tool itself

**Candidate names to explore**
- **Temporal** — already used in-app; clean, distinctive, slightly abstract
- **Podium** — evokes the presenter context
- **Cue** — short, implies a stage/performance signal
- **Pace** — echoes the "SET THE PACE" headline already in the UI
- **Spotlight** — suggests being on stage

**What a name change touches**
- `applicationId` in `build.gradle` (package rename)
- App label in `AndroidManifest.xml`
- Play Store listing title and description
- GitHub repo name / README
- `docs/` references and user manual

---

## Ideas / Wishlist

- **Export phases as JSON** — let users back up and share their phase configurations
- **Haptic feedback** — vibrate on phase change
- **Tablet / landscape layout** — wider timer with side panel for slide list
- **Tablet split-screen** — run timer alongside presentation notes

---

*Last updated: 2026-04-19*


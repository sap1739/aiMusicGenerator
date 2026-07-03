# Third-party review

Reviewed 2026-07-03. No source from the candidate applications is copied into Auralis.

| Project | License finding | Decision |
|---|---|---|
| ACE-Step 1.5 | Repository code is MIT; model artifacts must be checked at the selected model host | Preferred external REST inference engine; preserve upstream notices in its own deployment |
| fspecii/ace-step-ui | README claims MIT, but no root `LICENSE` was retrievable during review | UX research only; no code or assets reused |
| roblaughter/ace-step-studio | No license file/clear license found during review | No reuse |
| Facebook AudioCraft | Code MIT; model weights CC BY-NC 4.0 | Excluded from commercial path because the weights are non-commercial |
| AICoverGen | MIT | No reuse; voice conversion expands consent/abuse surface |
| Ultimate RVC | MIT | No reuse; defer voice cloning until evidence-based consent exists |

Runtime web packages keep their upstream licenses through normal package dependency metadata. The placeholder sparkle mark is supplied by Phosphor Icons (MIT).

This review is engineering guidance, not legal advice. Re-check the exact ACE-Step model card and all model/dependency licenses before commercial deployment.

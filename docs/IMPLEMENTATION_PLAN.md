# Phased implementation plan

1. **MVP foundation — implemented:** original brand, responsive studio, FastAPI, SQLite, local storage, demo generation, uploads, transforms, library, consent, tests, and CI.
2. **Inference deployment:** deploy the official ACE-Step REST server on a GPU worker, pin its release and model hashes, map all transform payloads in the adapter, and add Redis-backed durable jobs.
3. **Production data:** Postgres, S3-compatible storage, signed downloads, real authentication, quotas, audit logs, and deletion retention rules.
4. **Audio depth:** FFmpeg/librosa analysis, WaveSurfer regions, stem previews, version diffing, provenance manifests, and perceptual quality evaluation.
5. **Trust and scale:** moderation review tooling, voice-consent evidence, C2PA-style provenance, observability, billing, and GPU autoscaling.

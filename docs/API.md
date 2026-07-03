# API reference

Interactive OpenAPI documentation is available at `/docs` on the API service.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Service and engine readiness |
| POST | `/api/generate` | Create a text/lyrics generation job |
| POST | `/api/upload` | Upload authorized source audio |
| POST | `/api/cover` | Create an authorized cover version |
| POST | `/api/repaint` | Regenerate a selected time range |
| POST | `/api/stems` | Create stem versions |
| POST | `/api/vocal-to-bgm` | Generate accompaniment |
| GET | `/api/jobs/{job_id}` | Poll progress and result |
| GET | `/api/tracks` | Search/filter the library |
| GET | `/api/tracks/{track_id}` | Track detail and versions |
| PATCH | `/api/tracks/{track_id}` | Rename, favorite, or update tags |
| DELETE | `/api/tracks/{track_id}` | Delete track metadata and owned audio |
| GET | `/api/audio/{track_id}` | Stream/download audio with range support |

All generated results carry a provenance value: `ai_generated`, `uploaded`, `remix`, `cover`, `repaint`, `stems`, or `vocal_to_bgm`.

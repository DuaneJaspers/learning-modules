# Learning Modules

Offline-first learning content for the Modular Learning Android app.

## Structure

Each module is a directory containing:
- `module.json` — module manifest with sections, lessons, exercises, assessments, and flashcards
- `assets/` (optional) — images, audio, or other media referenced by lessons

## Module Index

`modules.json` at the repo root is the canonical index. The app fetches this to discover available modules.

## Contributing

1. Create a directory named after your module (e.g., `my-module/`)
2. Write `module.json` following the schema in the app's `ModuleModel.kt`
3. Add `modules.json` entry with correct SHA-256 checksum
4. Open a pull request

## Checksums

Each module entry includes a `sha256` checksum. The app validates this on download to detect corruption.

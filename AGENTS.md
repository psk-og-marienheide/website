<!-- (C) PSK OG Marienheide e.V., VR/Köln 1369 -->

# Repository instructions

These instructions apply to this club website repository. They supplement the
user's global instructions and do not authorize protected or remote operations.

## Site and content

- Maintain the static German Hugo site, authored in Markdown, with a small
  repository-owned theme. Preserve yellow/blue branding and support light/dark
  appearance following browser preference. Keep mobile and keyboard use accessible.
- Preserve existing content, dates, and media unless the user requests changes.
  Do not invent events, officers, contact details, or legal text. Keep historical
  events visibly historical and preserve legacy URLs where practical.
- Remove Gästebuch, Anmeldung zur KSA, and Kalender links from migrated navigation
  and repeated calls to action. Remove Dennis Schmidt and his associated team
  role/contact details, WordPress credits, and the three specified Terminschutzantrag
  download entries. Do not restore these through copied navigation or wrappers.
- Serve Downloads from local files with source/revision/checksum metadata. Keep
  Sachkundenachweis as NRW material using the selected Stadt Köln PDF, Stand Mai
  2019; do not substitute BH/VT training material or certificates.
- Impressum must include `Amtsgericht Köln, VR 1369`.
- Keep dog profiles on `/unsere-hunde/`, with aliases for the two former dog-page
  URLs. The unrendered `content/unsere-hunde-2-2/_index.md` keeps the memorial child
  at its existing URL; do not cascade its build settings to that child. Do not
  infer a dog's death from age alone.

## Privacy

- Never make visitors automatically load externally hosted assets: scripts, CSS,
  fonts, images, embedded maps/media, tracking, or resource hints. Use system fonts
  and local assets. Ordinary outbound navigation links are allowed. Use the shared
  `layouts/partials/link.html` renderer for external web links: new tab,
  `noopener noreferrer`, visible indicator and an accessible new-tab announcement.
- Build-time downloads may prepare local assets, but routine rendering must not
  silently update reviewed content or depend on live third-party forms/services.
- Check generated HTML, CSS, scripts, and browser requests. Source scanning alone
  does not prove absence of dynamically triggered external requests.

## Build and validation

- Use the minimal pinned Hugo 0.169.0 builder with Podman/Docker support. The
  only operator commands are `make serve` for loopback preview (including drafts)
  and `make build` for production rendering and static validation. Both share
  internal, announced image preparation; see [README.md](README.md) for commands,
  prerequisites, first-run effects, content editing and troubleshooting.
- Markdown is in `content/`, theme assets in `assets/`, and layouts/render hooks in
  `layouts/`. Parent sections use `_index.md`; page bundles use `index.md`. Keep
  original publication dates and notices on historical entries; evergreen pages
  need no date metadata. Migration IDs, source paths and imported timestamps
  belong in `data/migration-pages.json`. Preserve old URLs with aliases when
  moving migrated pages, and update migration/media paths. Reviewed PDFs and
  compatibility copies are in `static/`; provenance and outcomes are in `data/`.
- `tools/check-site.py` runs inside `make build`: check links/fragments, prefix
  escapes, automatic resources, retired content, all 27 source-page outcomes,
  required legal/download pages, register court, media checksums and reviewed PDF
  bytes including legacy URLs. Run focused checker regression tests when changing
  it. Rendering/checks run offline and replace `public/` only after success.
- `.github/workflows/pages.yml` validates PRs for root and prefix URLs; only a
  `main` push in `snazy/psk-og-marienheide` may publish. The publication conditions
  live in the build job; deployment uses its `publish` output and requires build
  success. There is no repository-variable switch or manual-deploy trigger.
  Pages must already be enabled with GitHub Actions as its source; metadata lookup
  has `enablement: false`. Build once at the Pages-provided base URL and deploy
  that exact checked artifact. Only deployment has Pages/OIDC write permissions.
  Keep Actions SHA-pinned, checkout credentials unpersisted, finite timeouts and
  production concurrency without cancelling active deployment.
- The owner's factual/legal review remains in
  [docs/review-checklist.md](docs/review-checklist.md). Preserve existing legal
  wording until reviewed; do not represent migration as legal validation. Hosted
  setup, domain cutover and rollback are in [docs/publishing.md](docs/publishing.md).
  Report hosted setup, actual workflow execution and domain verification separately
  from local implementation and tests; inspect current state before claiming them.
- Keep generated output/caches inside ignored checkout-local paths. Preserve host
  file ownership, quote bind paths, and expose preview ports only on loopback.
  Do not mount host home directories, credentials, or engine sockets.
- Validate both a domain-root base URL and a GitHub project-prefix URL. Deploy only
  from pushes to `main`; pull requests build/check without deployment permissions.
- Run checks proportional to the change and report unverified browser/hosted
  behavior. Do not install/configure tools or start services implicitly.

## Token usage

Be mindful of Codex token usage. Prefer targeted searches, bounded output, and
relevant excerpts. Avoid repeated full-file reads and redundant checks. Keep
updates concise without skipping necessary validation. Use agents only when
explicitly authorized.

## Ownership and source handling

- Newly authored files use `(C) PSK OG Marienheide e.V., VR/Köln 1369` in native
  comment syntax where supported, without injecting notices into visible content
  or binary files. This notice does not select an open-source license.
- Preserve third-party notices and redistribution requirements for copied/adapted
  code, PDFs, and other assets, including anything carried over from Buildish.
- `reference/` contains raw migration evidence, including retired content. Keep it
  out of commits and generated site output. Preserve user changes.
- Do not commit, push, publish, change GitHub settings/remotes, or alter domain/DNS
  configuration without explicit approval for the exact operation.

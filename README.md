<!-- (C) PSK OG Marienheide e.V., VR/Köln 1369 -->

# PSK OG Marienheide e.V.

German, Markdown-authored Hugo website with a local yellow/blue design, responsive
layouts, and automatic light/dark appearance. All browser assets are served locally.

**Current state:** content migration, local downloads, the theme and GitHub Pages
workflow are implemented. Complete the remaining factual/legal review using
[the review checklist](docs/review-checklist.md). At the last hosted check on
2026-11-10, [the repository](https://github.com/snazy/psk-og-marienheide) existed
on `main`, was private, and had Pages disabled; there were no workflow runs.
Local validation is complete, while hosted publication and domain cutover remain
unverified.

## Local inspection

Prerequisites: an existing Podman or Docker installation and GNU Make on Linux.
The wrapper prefers Podman; set `CONTAINER_ENGINE=docker` to choose Docker.

```sh
make serve
```

Open `http://127.0.0.1:1313/`. Changes reload automatically; Ctrl+C stops the
foreground container. Override the host port with `PORT=1414 make serve`.
Preview includes drafts. Without JavaScript, navigation and browser-preferred
light/dark appearance still work. The optional appearance selector stores only
its preference in browser localStorage.

## Production build

```sh
make build
```

This renders with Hugo 0.169.0, validates output, and replaces generated `public/`
only after success. Old generated files are removed. Build output is ignored by
Git and should not be edited. Override the URL for project-prefix validation:

```sh
BASE_URL=https://example.invalid/club/ make build
```

The only operator commands are `serve` and `build`. Both internally prepare/reuse
the builder image. The first run downloads the pinned Python base and checksum-
verified Hugo binary and writes several hundred MB to the engine's image storage.
Changed Containerfile inputs select a new image; there is no registry login or
image publication. Initial preparation requires network; production rendering and
checks run without network. Output, Hugo resources, and cache stay under `build/`
and `public/`; the container does not mount host home or credentials. Linux output
belongs to the invoking user. SELinux hosts may require an explicitly approved
mount-label adjustment. Tool installation, engine configuration and protected
image/storage operations require the operator's applicable authorization.

## Editing pages and photos

- Pages are Markdown in `content/`. Their TOML front matter contains titles and
  descriptions. Keep original publication dates on news and historical entries;
  evergreen pages need no date metadata. Set `lastmod` only when maintaining an
  accurate update date. Migration IDs, source paths and imported timestamps live
  in `data/migration-pages.json`. A section with child pages uses `_index.md`;
  an individual page bundle uses `index.md`.
- Ordinary local links such as `[Unser Team](/ueber-uns/unser-team-2/)` work at
  both domain-root and project-prefix URLs through the local link render hook.
- External HTTP(S) links automatically open in a new tab, with a visible arrow
  and a screen-reader announcement. Use ordinary Markdown links; no special
  syntax is needed. Internal, email and phone links retain their normal behavior.
- Add photos beside the page's Markdown file. Use `![Description](photo.jpg)` for
  an inline photo, or
  `{{< photo file="photo.jpg" alt="Description" caption="Caption" >}}` to add
  an original-size link and caption. Hugo generates local WebP display versions.
  Shared images in `assets/` can use their asset-relative path, for example
  `![FCI, VDH und PSK](images/fci-vdh-psk.png)`.
  Gallery entries use `[[gallery]]` front-matter tables in `content/galerie/`.
- All 22 dog profiles and their photos are in `content/unsere-hunde/`. Edit that
  combined page; its aliases redirect the former dog-page URLs. Memorial entries
  remain separate under `content/unsere-hunde-2-2/in-memoriam/`. Keep the unrendered
  `content/unsere-hunde-2-2/_index.md` so its child retains its URL.
- The shared homepage photo, CSS and theme/menu script live in `assets/`; layouts
  and Markdown render hooks are in `layouts/`. The shared banner and transparent
  dog-head logo are in `assets/images/`. The site uses system fonts.
- Main navigation is in `hugo.toml`; related page links are in Markdown and the
  footer is in `layouts/baseof.html`. Mark historical events `historical = true`.
- `reference/` holds ignored migration evidence and is not a build dependency.
  Preserve original photo/PDF notices. The club copyright notice grants no license.

## Updating downloads

Reviewed PDFs live in `static/downloads/`. Each entry in `data/downloads.json`
records title, source URL/publisher, revision, retrieval date, byte count, SHA-256,
site path and legacy URLs. Copy reviewed replacement bytes to both the ordinary
file and each compatibility path under `static/`, update that metadata, and run
`make build`. No build fetches or silently updates documents. The selected
Sachkundenachweis is the Stadt Köln NRW question catalogue, Stand Mai 2019.

`data/migration-assets.json` records copied media checksums, and
`data/migration-pages.json` records the outcome of all 27 source pages/posts.
When moving a migrated page, retain its original URL with front-matter `aliases`,
update its `target_path` in the migration map, and update any moved media paths.
If intentionally updating a copied source photo, update its provenance entry too.

## Checks and troubleshooting

`make build` checks local links/fragments, project-prefix escapes, automatic
resource origins, CSS/JS resource references, retired content, migration outcomes,
legacy routes, required legal/download pages, register court, media checksums and
reviewed PDF bytes at ordinary and compatibility URLs. Correct reported content,
links or metadata in source and rebuild; preserve the last successful `public/` output.

For contributors with Hugo 0.169.0 and Python already installed, validation can
also run without image preparation:

```sh
HUGO_RESOURCEDIR="$PWD/build/resources" hugo --baseURL https://example.invalid/ \
  --destination "$PWD/build/native" --cleanDestinationDir \
  --cacheDir "$PWD/build/cache" --noBuildLock --minify --panicOnWarning
python3 tools/check-site.py build/native https://example.invalid/
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py'
```

If no engine is available, install/configure one separately. Failed first-run
image preparation needs network access to the pinned base and Hugo archive;
rendering then runs offline. A PDF checksum failure requires reviewing the file
and provenance rather than bypassing the check. A missing layout or content link
usually indicates a mistaken bundle/section name or a path that needs correcting.

Local validation includes native and Podman root/project-prefix builds, 11 checker
regression tests, and isolated Chrome checks. The initial full-page browser matrix
covered 1440px, 720px, 390px and 320px, themes/storage, menu/Escape, no-JS and print.
Later focused checks verified the shared banner/logo, all 22 combined dog profiles,
legacy redirects and external links. External-link checks covered keyboard
activation, a separate tab with no opener, and no-JS behavior. No horizontal
overflow, broken images, automatic external requests or browser errors were found
in those checks. Test browsers were stopped; existing user previews were preserved.
Docker and arm64 runtime, Firefox/Safari, real devices, actual desktop 200% browser
zoom, a full accessibility audit and hosted workflow execution remain unverified.

## Publishing

[Publishing, domain cutover and rollback](docs/publishing.md) describes the
reviewable `.github/workflows/pages.yml`. PRs build/check root and project-prefix
URLs with no deployment write permissions. A push to `main` builds once for the
existing Pages base URL, uploads checked `public/`, and a separate job deploys
that same artifact. Only deployment has Pages/OIDC write permissions. Actions
are SHA-pinned, credentials are not persisted, and jobs have finite timeouts.

Publication is restricted to `snazy/psk-og-marienheide` by a literal repository-name
check. The build job decides whether to publish; deployment consumes its output
and runs only after build success. No repository variable is needed. Other
repositories and pull requests validate without uploading or deploying a Pages
artifact. The workflow uses Docker on `ubuntu-26.04` runners; hosted execution has
not yet been verified.

For the GitHub-hosted preview:

1. Make the repository public for GitHub Free, or retain private visibility with
   an eligible plan. The published website is normally public either way.
2. In **Settings → Pages → Build and deployment**, choose **GitHub Actions**.
   The workflow reads existing Pages settings and does not enable Pages itself.
3. Configure the `github-pages` environment for `main`, without a required reviewer
   or wait timer if publication should be automatic, then push the reviewed site
   and workflow to `main`. There is no manual-deploy trigger.
4. Check the build/deploy result and returned site URL. Without a custom domain,
   the expected preview is <https://snazy.github.io/psk-og-marienheide/>.

The production build takes its base URL from Pages metadata, overriding the local
club-domain default. Club-domain/DNS cutover is separate from the preview. No
registry workflow or tracked `CNAME` file is needed. Hosted setup, pushes and
publication by an agent require the applicable operation-specific authorization.

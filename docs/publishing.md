<!-- (C) PSK OG Marienheide e.V., VR/Köln 1369 -->

# GitHub Pages setup and domain cutover

Workflow and rollout checklist for `snazy/psk-og-marienheide`, default branch
`main`. At the last hosted check on 2026-11-10, the repository existed and was
private, with Pages disabled and no workflow runs. Publication and domain cutover
remain unverified. Recheck current provider settings and DNS targets at rollout.

## GitHub setup

The workflow in `.github/workflows/pages.yml` validates pull requests for root and
project-prefix URLs. A `main` push in the configured production repository renders
once at the existing Pages base URL and deploys that exact checked artifact.
The production repository is selected by the literal name
`snazy/psk-og-marienheide` in the build job's publication condition. Deployment
uses that job's `publish` output and requires build success. No repository variable
is required. Other repositories and PRs run validation only. The workflow reads
existing Pages metadata with `enablement: false`; enable Pages before the first
production run. It does not create or enable the hosted site automatically.

Before enabling publication, complete [the content review](review-checklist.md).
The current legal text is migrated source text, not a completed legal/hosting review.

The existing project repository is sufficient; no `snazy.github.io` repository is
needed. Public source supports GitHub Free; private source needs an eligible plan
and does not by itself make the published website private.

Setup sequence, each mutation subject to exact-operation authorization:

1. Review the existing repository's visibility and choose public for GitHub Free,
   or retain private visibility with an eligible plan. Publish only reviewed
   source, local assets and workflow files; keep `reference/` excluded.
2. In repository **Settings → Pages**, select **GitHub Actions** as the build and
   deployment source. Do not select a publishing branch or grant blanket workflow
   write access. Ensure repository/org Actions policy permits the chosen Actions.
3. Configure the `github-pages` environment to allow deployments from branch
   `main` only. Do not require a manual reviewer or wait timer: those would prevent
   the requested automatic publication on a successful main push.
4. Push the reviewed implementation under explicit authorization and verify the
   first build/deploy at the URL returned by Pages. Before a custom domain, this
   will normally be `https://snazy.github.io/psk-og-marienheide/`. The main push
   triggers the workflow; enabling Pages alone does not trigger this push-only
   workflow. The production base URL comes from Pages metadata and overrides the
   local Hugo club-domain default.
5. Optionally protect `main` using a PR and the actual build status check once it
   exists. This governs how changes reach main; it does not add deployment approval.

Source visibility, hosting availability, HTTPS and public accessibility are covered
by [GitHub Pages HTTPS guidance](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).
Environment branch restrictions are described in
[deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

## Domain cutover

Recommended canonical host: `www.psk-og-marienheide.de`, retaining the present
host. Configure the apex domain to redirect to it through Pages. Keep the current
DNS provider; moving nameservers is unnecessary for this migration.

Before switching, export current DNS records and identify web, mail, and other
services using them. Preserving MX records alone is insufficient if their targets
or mail clients depend on an apex address that will change. Plan those dependencies
before changing web records. Record rollback values and retain the old web host.

1. In the owning account/organization **Settings → Pages**, verify
   `psk-og-marienheide.de` using GitHub's supplied TXT challenge. Keep the TXT record.
   This is account/org verification, separate from repository configuration. See
   [domain verification](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages).
2. At cutover, save `www.psk-og-marienheide.de` in repository **Settings → Pages →
   Custom domain** before pointing web DNS at Pages. Actions publishing requires
   no tracked `CNAME` file; GitHub ignores one for this publishing mode.
3. Set web DNS as below. `www` points to `snazy.github.io`, without a URL scheme
   or repository path. Replace conflicting old web records after dependency review;
   preserve unrelated records and do not add wildcard routing.

| Name | Type | Proposed target |
| --- | --- | --- |
| `www` | CNAME | `snazy.github.io.` |
| `@` | A | `185.199.108.153` |
| `@` | A | `185.199.109.153` |
| `@` | A | `185.199.110.153` |
| `@` | A | `185.199.111.153` |

Optional IPv6 uses the four GitHub Pages AAAA targets. If enabled, replace old
web AAAA records too; stale IPv6 must not keep serving the old site. DNS targets,
Actions `CNAME` behavior and automatic apex/`www` redirects are documented in
[custom domain configuration](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

4. Rebuild through the main-push workflow using the final Pages base URL. A custom
   domain changes the site from a repository prefix to `/`; check canonical links,
   sitemap, assets, downloads, and legacy aliases again. Coordinate this with DNS.
5. Wait for DNS validation/certificate provisioning, then enable **Enforce HTTPS**.
   Check both hostnames over HTTP/HTTPS, apex-to-`www` redirects, key old URLs,
   local asset requests, downloads, and mail delivery. Certificate provisioning
   and DNS propagation can take time; do not promise a zero-interruption switch.
   See [HTTPS provisioning](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).

For rollback, restore the recorded old web DNS and verify the old site, then
restore the staging URL/build configuration if Pages should remain usable there.
Keep verification TXT and unrelated DNS intact. If retiring Pages permanently,
remove web DNS pointing to it before unbinding/deleting the Pages site. Perform
rollback mutations only under the applicable explicit authorization.

## Optional follow-up after gaining full domain control

- [ ] Remind the user that they can set up `psk-og-marienheide.de` mail groups
  using their own Google Workspace. Agree on desired group addresses and members
  before any setup. This is separate from the website migration and does not
  block publication. The reminder does not authorize account or mail/DNS changes.

## Handoff

Record the chosen repository, Pages/environment settings, required status check,
successful deployment URL/run, canonical domain, DNS values/previous values,
certificate status, and outstanding checks. Keep credentials out of these notes.
Keep README and root `AGENTS.md` accurate after rollout.

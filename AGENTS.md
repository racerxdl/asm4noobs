# AGENTS.md — asm4noobs

## Project overview

Jekyll static site for an Assembly language tutorial (Portuguese/ptbr). Theme: `tale`. Hosted on GitHub Pages at `asm.lucasteske.dev`.

## Dev commands

```bash
bundle install                  # install gems (Ruby + Bundler required)
bundle exec jekyll serve        # start dev server at http://localhost:4000
```

No Makefile, no Node/npm, no test suite. CI deploys from `master` via `.github/workflows/build.yml` on push.

## Content architecture (critical)

**All actual content lives in `_i18n/ptbr/`.** Top-level `.md` pages are stubs with Jekyll front matter that delegate with `{% translate_file %}`. To edit a page:

- Front matter → edit the top-level file (e.g. `index.md`, `contributing.md`, `404.md`)
- Body content → edit the matching file in `_i18n/ptbr/` (e.g. `_i18n/ptbr/index.md`)

Posts live exclusively in `_i18n/ptbr/_posts/` with names like `YYYY-MM-DD-slug.md`. There are no top-level post stubs.

`opcodes/` pages have the same pattern: stub at `opcodes/index.md`, content at `_i18n/ptbr/opcodes/`.

## i18n setup

Uses `jekyll-multiple-languages-plugin`. Only language: `ptbr`. Translation strings in `_data/pt.yml` and `_i18n/ptbr.yml`. The `exclude_from_localizations` config in `_config.yml` skips `javascript`, `images`, `css`, and `assets` directories.

## Sitemap / SEO

`jekyll-seo-tag` and `jekyll-sitemap` are active. `_config.yml` has Open Graph / Twitter card config. Sitemap is at `sitemap_index.xml`, search at `search.json`.

## Custom Liquid filter

`_plugins/dec_to_hex.rb` — `{{ value | dec_to_hex }}` converts decimal to `0xNN` hex string.

## Syscall data generation

`_generator/` contains Python 3 scripts that fetch syscall tables from Linux kernel and Darwin XNU sources and output JSON to `_data/`:

- `syscall-linux-amd64.py` — requires `GH_READ_TOKEN` env var (GitHub PAT) to avoid API rate limits. Reads from `resource.cache` for avoiding repeated fetches. Outputs `_data/syscalls_linux_amd64.json`.
- `syscall-darwin-amd64.py` — no auth needed. Outputs `_data/syscalls_darwin_amd64.json`.

Both scripts also save outputs to root-level `syscalls_*.json` (used at runtime by Jekyll pages). Run them from the repo root.

## Commit conventions

Every commit message must end with:

```
 🤖 Generated with Mister Maluco

Co-Authored-By: MisterMal <teskeslab@lucasteske.dev>
```

When creating GitHub PRs, issues, or comments via `gh`/`tea` CLI, append `Automated by MisterMal` to the body.

## Config quirks

- `jekyll-spaceship` is configured with media-processor (iframe defaults) and emoji-processor in `_config.yml`.
- `jekyll-graphviz` is in the Gemfile's `:jekyll_plugins` group but NOT in `_config.yml` plugins list.
- `jekyll-paginate` appears twice in the plugins list (duplicate), harmless but don't add a third.
- Permalink format: `/:year/:month/:title` (Jekyll default is different).
- `liquid` 4.0.3 is incompatible with Ruby 3.x (`String#tainted?` removed). If you get `undefined method 'tainted?'`, run `bundle update liquid` to get 4.0.4+.

# Creating and pushing the public repo

Run these from inside the `qss20repo` folder. Rename the folder first if you
want a different repo name.

## Option A — with the GitHub CLI (easiest)

```bash
cd qss20repo
git init
git add .
git commit -m "Milestone 2: WHO capacity/burden pipeline, three RQs, figures"
gh repo create qss20-neuro-access --public --source=. --remote=origin --push
```

If `gh` is not installed: `brew install gh` then `gh auth login`.

## Option B — without the CLI

1. Create a new **public** repo on github.com named `qss20-neuro-access`.
   Do not add a README, .gitignore, or license — the folder already has them.
2. Then:

```bash
cd qss20repo
git init
git add .
git commit -m "Milestone 2: WHO capacity/burden pipeline, three RQs, figures"
git branch -M main
git remote add origin https://github.com/<your-username>/qss20-neuro-access.git
git push -u origin main
```

## Before you submit

- Paste the repo URL into your milestone writeup.
- Confirm the repo is **public** (Settings → General → Danger Zone shows
  "Change visibility").
- Check that the three PNGs in `output/` render on the GitHub page.
- `data/raw/neurology_atlas_2017.pdf` and the DHS `urlslist*.txt` are
  gitignored on purpose. If your professor wants the Atlas PDF included, remove
  those two lines from `.gitignore`. Do **not** commit DHS microdata or the
  manifest — the URLs are tied to your account.

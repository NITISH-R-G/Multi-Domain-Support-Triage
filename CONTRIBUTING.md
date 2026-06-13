# Contributing to HackerRank Orchestrate

First off, thank you for considering contributing to HackerRank Orchestrate. It's people like you that make HackerRank Orchestrate such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## Fork & create a branch

If this is something you think you can fix, then fork HackerRank Orchestrate and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-japanese-translations
```

## Get the test suite running

Make sure you're using Python 3.11+. We recommend using a virtual environment.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r code/requirements.txt
```

Run tests to ensure everything is working correctly before you begin:

```sh
mkdir -p code/.cache
cd code/
python -m pytest tests -q
```

## Implement your fix or feature

At this point, you're ready to make your changes. Feel free to ask for help; everyone is a beginner at first.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with HackerRank Orchestrate's master branch:

```sh
git remote add upstream git@github.com:hackerrank/orchestrate.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 325-add-japanese-translations
git rebase master
git push --set-upstream origin 325-add-japanese-translations
```

Finally, go to GitHub and make a Pull Request.

## Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

## Coding Style

* Please follow standard Python PEP 8 style guidelines.
* We use Ruff for code formatting and linting. You can format your code using: `ruff format .`
* We use Mypy for static type checking.
* The repository's AI maintainer will also review your code for best practices!

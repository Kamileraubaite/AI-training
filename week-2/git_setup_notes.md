# Git Setup Notes

You created a new project folder and moved into it:

```bash
mkdir my-project
cd my-project/
```

You checked the folder contents with:

```bash
ls
```

At that point, the folder was empty.

You then initialized a new Git repository:

```bash
git init
```

Git created a hidden `.git` folder and started the repository on the default branch `master`.

You checked the repository status with:

```bash
git status
```

This confirmed there were no commits and no files being tracked yet.

You renamed the branch from `master` to `main`:

```bash
git branch -m main
```

You checked again with:

```bash
git status
```

and confirmed you were now on the `main` branch.

You created a blank README file:

```bash
touch README.md
```

Then checked the folder:

```bash
ls
```

Git showed `README.md` as an **untracked file**, meaning the file existed but Git was not tracking it yet.

You then created a blank Python file:

```bash
touch main.py
```

The project now contained:

```text
README.md
main.py
```

You staged all files using:

```bash
git add .
```

This moved the files into Git's **staging area**, ready to be committed.

You checked this with:

```bash
git status
```

and Git showed both files under:

```text
Changes to be committed
```

You created your first commit:

```bash
git commit -m "Initial commit: add blank README and main.py"
```

This saved a snapshot of the two files into the repository's history.

You then tried:

```bash
git log --online
```

but this failed because the correct flag is:

```bash
git log --oneline
```

`--oneline` gives a shorter version of the Git history, for example:

```text
8d998f0 Initial commit: add blank README and main.py
```

You also used:

```bash
git log
```

which showed the full commit information, including:

- commit hash
- author
- date
- commit message

You then connected your local repository to a GitHub repository by adding a remote called `origin`:

```bash
git remote add origin https://github.com/Kamileraubaite/my-project.git
```

You checked the remote connection with:

```bash
git remote -v
```

This showed the GitHub URL being used for both fetching and pushing.

You checked the repository again:

```bash
git status
```

and saw:

```text
nothing to commit, working tree clean
```

This means all current changes had been committed.

Finally, you pushed your local `main` branch to GitHub:

```bash
git push -u origin main
```

The `-u` sets `origin/main` as the upstream branch, so after the first push you can usually use:

```bash
git push
```

without having to specify `origin main` every time.

## Key Git Concepts You Practised

- **Repository** — a project tracked by Git.
- **Branch** — a version or line of development, such as `main`.
- **Untracked file** — a file Git knows exists but is not tracking yet.
- **Staging area** — files prepared for the next commit.
- **Commit** — a saved snapshot of your project.
- **Remote** — a connection to a repository hosted elsewhere, such as GitHub.
- **Push** — sends local commits to the remote repository.
- **Working tree clean** — there are currently no uncommitted changes.

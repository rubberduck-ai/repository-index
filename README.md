# Repository Index

Indexes a Git repository using embeddings.

## Setup

`pip install -r requirements_dev.txt`

## Run

`python3 path-to/repository_index/repository_index.py`

Example:
`python3 ~/github/repository-index/repository_index/repository_index.py`

> _Tip: set an alias in your `.bashrc` or `.zshrc` to make it easier to run._

`echo "alias indexrepo='python3 ~/github/repository-index/repository_index/repository_index.py'" >> ~/.zshrc`

This assumes that the `repository_index.py` script is located in the `~/github/repository-index/repository_index/` directory. If you're using `bash` instead of `zsh`, you should add the alias to your `.bashrc` file instead.

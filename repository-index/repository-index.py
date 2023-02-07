import argparse
from git import Repo


def is_valid_file(filename):
    return (
        filename.endswith(".ts")
        or filename.endswith(".js")
        or filename.endswith(".tsx")
        or filename.endswith(".sh")
        or filename.endswith(".py")
        or filename.endswith(".md")
        or filename.endswith(".json")
        or filename.endswith(".yml")
        or filename.endswith(".yaml")
        or filename.endswith(".html")
        or filename.endswith(".css")
        or filename.endswith(".scss")
        or filename.endswith(".less")
        or filename.endswith(".xml")
        or filename.endswith(".java")
        or filename.endswith(".cs")
        or filename.endswith(".cpp")
        or filename.endswith(".c")
        or filename.endswith(".h")
        or filename.endswith(".go")
        or filename.endswith(".php")
        or filename.endswith(".rb")
        or filename.endswith(".swift")
        or filename.endswith(".kt")
        or filename.endswith(".dart")
        or filename.endswith(".sql")
        or filename.endswith(".graphql")
        or filename.endswith(".gql")
        or filename.endswith(".txt")
    ) and not (
        filename.endswith(".min.js")
        or filename.endswith(".min.css")
        or filename.endswith("pnpm-lock.yaml")
    )


parser = argparse.ArgumentParser(description="Repository Index")

parser.add_argument(
    "--repository-path", type=str, help="Git repository path", required=True
)
parser.add_argument("--output-file", type=str, help="Output file", required=True)
parser.add_argument("--open-ai-api-key", type=str, help="OpenAI API key", required=True)

args = parser.parse_args()

print(args)

repo = Repo(args.repository_path)
allFiles = repo.git.ls_files().split("\n")


result = list(filter(is_valid_file, allFiles))

print(result)

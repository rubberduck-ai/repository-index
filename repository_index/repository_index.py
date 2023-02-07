import argparse

from split_linear_lines import split_linear_lines
from is_supported_file import is_supported_file
from git import Repo

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


result = list(filter(is_supported_file, allFiles))

chunks_with_embedding = []

for file in result:
    with open(args.repository_path + "/" + file, "r") as f:
        content = f.read()
        chunks = split_linear_lines(content, 150)
        for chunk in chunks:
            chunks_with_embedding.append(
                {
                    "start_position": chunk["start_position"],
                    "end_position": chunk["end_position"],
                    "content": chunk["content"],
                    "file": file,
                }
            )

print(chunks_with_embedding[-1])

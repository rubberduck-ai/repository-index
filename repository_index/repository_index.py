import argparse
import json
import os
from pathlib import Path

import openai
from git import Repo
from is_supported_file import is_supported_file
from split_linear_lines import split_linear_lines


api_key_path = Path.home() / ".openai" / "api_key"

if not api_key_path.exists():
    choice = input(
        "OpenAI API key not found. Do you want to create a new API key file? (y/n) "
    ).lower()
    if choice == "y":
        api_key = input("Please enter your OpenAI API key: ").strip()
        api_key_path.parent.mkdir(parents=True, exist_ok=True)
        with open(api_key_path, "w") as f:
            f.write(api_key)
            print(f"API key saved to {api_key_path}")
    else:
        raise ValueError("OpenAI API key is required to run this script.")

with open(api_key_path) as f:
    openai.api_key = f.read().strip()

parser = argparse.ArgumentParser(description="Repository Index")

parser.add_argument(
    "--repository-path", type=str, help="Git repository path", required=True
)
parser.add_argument(
    "--output-file",
    type=str,
    help="Output file path",
    default="./.rubberduck/embedding/result.json",
)

args = parser.parse_args()

if os.path.exists(args.repository_path):
    repo = Repo(args.repository_path)
    allFiles = repo.git.ls_files().split("\n")
else:
    raise ValueError("Invalid repository path")

result = list(filter(is_supported_file, allFiles))

chunks_with_embedding = []
token_count = 0

for file in result:
    with open(args.repository_path + "/" + file, "r") as f:
        content = f.read()
        chunks = split_linear_lines(content, 150)
        for chunk in chunks:
            chunk_start = chunk["start_position"]
            chunk_end = chunk["end_position"]

            print(f"Generating embedding for chunk '{file}' {chunk_start}:{chunk_end}")

            result = openai.Embedding.create(
                engine="text-embedding-ada-002", input=chunk["content"]
            )

            chunks_with_embedding.append(
                {
                    "start_position": chunk_start,
                    "end_position": chunk_end,
                    "content": chunk["content"],
                    "file": file,
                    "embedding": result.data[0].embedding,
                }
            )

            token_count += result.usage.total_tokens

output_file_path = args.output_file

if os.path.exists(os.path.dirname(output_file_path)):
    if os.path.exists(output_file_path):
        choice = input(
            f"{output_file_path} already exists. Do you want to overwrite it? (y/n) "
        ).lower()
        if choice != "y":
            print("Exiting without writing output file")
            exit()

    with open(output_file_path, "w") as f:
        f.write(
            json.dumps(
                {
                    "version": 0,
                    "embedding": {
                        "source": "openai",
                        "model": "text-embedding-ada-002",
                    },
                    "chunks": chunks_with_embedding,
                }
            )
        )

    print(f"Output saved to {output_file_path}")
else:
    raise ValueError("Invalid output file path")

cost = (token_count / 1000) * 0.0004

print()
print(f"Tokens used: {token_count}")
print(f"Cost: {cost} USD")

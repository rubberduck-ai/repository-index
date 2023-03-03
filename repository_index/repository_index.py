import argparse
import json
import os
import time
import datetime
from pathlib import Path

import openai
from git import Repo
from is_supported_file import is_supported_file
from split_linear_lines import split_linear_lines


api_key_path = Path.home() / ".openai" / "api_key"

if not api_key_path.exists():
    choice = input(
        "OpenAI API key file not found at ~/.openai/api_key. Create new API key file? (y/n) "

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
    "--repository-path", type=str, help="Git repository path",
)
parser.add_argument(
    "--output-file",
    type=str,
    help="Output file path",
    default="./.rubberduck/embedding/result.json",
)

args = parser.parse_args()

output_file_path = args.output_file

if args.repository_path is None:
    while True:
        repo_path = input("Please enter the path to the Git repository you want to index (enter '.' for the current directory): ")
        if not repo_path:
            print("I'm sorry, but the repository path can't be empty. Please try again.")
            continue
        if repo_path == ".":
            args.repository_path = os.getcwd()
            break
        if os.path.exists(repo_path):
            args.repository_path = repo_path
            break
        else:
            choice = input("I'm sorry, but that path is invalid. Would you like to try again? (y/n)").lower()
            if choice != "y":
                print("Alright, I'll stop here. Goodbye! 👋")
                exit()



if os.path.exists(args.repository_path):
    repo = Repo(args.repository_path)
    allFiles = repo.git.ls_files().split("\n")
else:
    raise ValueError("Invalid repository path")

result = list(filter(is_supported_file, allFiles))


if os.path.exists(os.path.dirname(output_file_path)):
    if os.path.exists(output_file_path):
        file_age = time.time() - os.path.getmtime(output_file_path)
        file_age_str = datetime.timedelta(seconds=int(file_age))
        file_age_str = str(file_age_str).split(".")[0]
        hours, remainder = divmod(int(file_age), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours == 0:
            timestamp = f"{minutes} minutes and {seconds} seconds ago"
        else:
            timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(output_file_path)).strftime('%-m-%-d-%Y at %-I:%M %p')
            timestamp += f" ({hours} hours, {minutes} minutes, and {seconds} seconds ago)"
        choice = input(
            f"\n🚨 Oops! It looks like the embedding file already exists at {output_file_path} 🚨\n\nYour repository was last indexed {timestamp}. \n\nWould you like to re-index your repository now? (y/n) "
        ).lower()
        if choice != "y":
            print("Alright, I won't re-index your repository. Goodbye! 👋")
            exit()
    else:
        print(f"Creating a new index file for your repository at {output_file_path}.")
else:
    raise ValueError(f"Invalid output file path: {output_file_path}")

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

if os.path.exists(output_file_path):
    print(f"Overwriting the index file at {output_file_path}")
else:
    try:
        os.makedirs(os.path.dirname(output_file_path))
    except OSError as exc:
        raise ValueError(f"Invalid output file path: {output_file_path}") from exc

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

cost = (token_count / 1000) * 0.0004

print()
print(f"Tokens used: {token_count}")
print(f"Cost: {cost} USD")

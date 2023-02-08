import argparse
import json

import openai
from git import Repo
from is_supported_file import is_supported_file
from split_linear_lines import split_linear_lines

parser = argparse.ArgumentParser(description="Repository Index")

parser.add_argument(
    "--repository-path", type=str, help="Git repository path", required=True
)
parser.add_argument("--output-file", type=str, help="Output file", required=True)

args = parser.parse_args()

repo = Repo(args.repository_path)
allFiles = repo.git.ls_files().split("\n")

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

with open(args.output_file, "w") as f:
    f.write(
        json.dumps(
            {
                "version": 0,
                "embedding": {
                    "source": "open-ai",
                    "model": "text-embedding-ada-002",
                },
                "chunks": chunks_with_embedding,
            }
        )
    )

cost = (token_count / 1000) * 0.0004

print()
print(f"Tokens used: {token_count}")
print(f"Cost: {cost} USD")

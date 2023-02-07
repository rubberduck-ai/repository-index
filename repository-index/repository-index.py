import argparse

parser = argparse.ArgumentParser(description='Repository Index')

parser.add_argument('--repository-path', type=str, help='Git repository path', required=True)
parser.add_argument('--output-file', type=str, help='Output file', required=True)
parser.add_argument('--open-ai-api-key', type=str, help='OpenAI API key', required=True)

args = parser.parse_args()

print(args)

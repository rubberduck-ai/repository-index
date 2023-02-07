import { Option } from "commander";
import fs from "node:fs/promises";
import { simpleGit } from "simple-git";
import zod from "zod";
import { Chunk } from "./chunk/Chunk";
import { createSplitLinearLines } from "./chunk/splitLinearLines";
import { OpenAIClient } from "./open-ai/OpenAIClient";
import { runProgram } from "./program/runProgram";

runProgram({
  name: "Repository Index",
  configurationOptions: [
    new Option(
      "--repository-path <string>",
      "Git repository path"
    ).makeOptionMandatory(),
    new Option(
      "--output-file <string>",
      "Name of the output file"
    ).makeOptionMandatory(),
    new Option("--open-ai-api-key <string>", "OpenAI API key")
      .env("OPEN_AI_API_KEY")
      .makeOptionMandatory(),
  ],
  configurationSchema: zod.object({
    repositoryPath: zod.string(),
    outputFile: zod.string(),
    openAiApiKey: zod.string(),
  }),
  async run({ repositoryPath, outputFile, openAiApiKey }) {
    const openAiClient = new OpenAIClient({
      apiKey: openAiApiKey,
    });

    const git = simpleGit({
      baseDir: repositoryPath,
      binary: "git",
      maxConcurrentProcesses: 6,
      trimmed: false,
    });

    const files = (await git.raw(["ls-files"])).split("\n");

    const chunksWithEmbedding: Array<
      Chunk & {
        file: string;
        embedding: Array<number>;
      }
    > = [];

    let tokenCount = 0;

    for (const file of files) {
      if (!isSupportedFile(file)) {
        continue;
      }

      const content = await fs.readFile(`${repositoryPath}/${file}`, "utf8");

      const chunks = createSplitLinearLines({
        maxChunkCharacters: 150,
      })(content);

      for (const chunk of chunks) {
        console.log(
          `Generating embedding for chunk '${file}' ${chunk.startPosition}:${chunk.endPosition}`
        );

        try {
          const embeddingResult = await openAiClient.generateEmbedding({
            input: chunk.content,
          });

          chunksWithEmbedding.push({
            file,
            ...chunk,
            embedding: embeddingResult.embedding,
          });

          tokenCount += embeddingResult.usage.totalTokens;
        } catch (error) {
          console.error(error);

          console.log(
            `Failed to generate embedding for chunk '${file}' ${chunk.startPosition}:${chunk.endPosition}`
          );
        }
      }
    }

    await fs.writeFile(outputFile, JSON.stringify(chunksWithEmbedding));

    console.log();
    console.log(`Tokens used: ${tokenCount}`);
    console.log(`Cost: ${(tokenCount / 1000) * 0.0004} USD`);
  },
});

function isSupportedFile(file: string) {
  return (
    (file.endsWith(".js") ||
      file.endsWith(".ts") ||
      file.endsWith(".tsx") ||
      file.endsWith(".sh") ||
      file.endsWith(".yaml") ||
      file.endsWith(".yml") ||
      file.endsWith(".md") ||
      file.endsWith(".css") ||
      file.endsWith(".json") ||
      file.endsWith(".toml") ||
      file.endsWith(".config")) &&
    !(
      file.endsWith(".min.js") ||
      file.endsWith(".min.css") ||
      file.endsWith("pnpm-lock.yaml")
    )
  );
}

import { Option } from "commander";
import { simpleGit } from "simple-git";
import zod from "zod";
import { runProgram } from "./program/runProgram";

runProgram({
  name: "Repository Index",
  configurationOptions: [
    new Option(
      "--repository-path <string>",
      "Git repository path"
    ).makeOptionMandatory(),
  ],
  configurationSchema: zod.object({
    repositoryPath: zod.string(),
  }),
  async run({ repositoryPath }) {
    const git = simpleGit({
      baseDir: repositoryPath,
      binary: "git",
      maxConcurrentProcesses: 6,
      trimmed: false,
    });

    const files = (await git.raw(["ls-files"])).split("\n");

    for (const file of files) {
      console.log(file);
    }
  },
});

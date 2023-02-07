import { Command, Option } from 'commander';
import { Schema } from 'zod';

export async function runProgram<T>({
  name,
  configurationOptions,
  configurationSchema,
  run,
}: {
  name: string;
  configurationOptions: Array<Option>;
  configurationSchema: Schema<T>;
  run: (configuration: T) => Promise<void>;
}) {
  const command = new Command();

  command.description(name);

  for (const option of configurationOptions) {
    command.addOption(option);
  }

  command.parse(process.argv);

  await run(configurationSchema.parse(command.opts()));
}

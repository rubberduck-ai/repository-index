import { runProgram } from "./program/runProgram";
import zod from 'zod';

runProgram({
  name: 'Repository Index',
  configurationOptions: [ ],
  configurationSchema: zod.object({}),
  async run({}) {
    console.log('Hello, world!');
  }
});

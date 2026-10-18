// Delete the end-to-end database so each run starts from the seed data.
import { rmSync } from "node:fs";

rmSync("e2e/test.db", { force: true });

import { defineConfig } from "orval";

export default defineConfig({
  japanTravel: {
    input: "../../apps/api/openapi.json",
    output: {
      target: "./src/generated.ts",
      client: "fetch",
    },
  },
});

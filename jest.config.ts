import type { Config } from "jest"
import nextJest from "next/jest.js"

// next/jest wires up SWC transforms, CSS/asset mocks, tsconfig paths, and env loading
// so tests run against the same toolchain as `next build`.
const createJestConfig = nextJest({ dir: "./" })

const config: Config = {
  testEnvironment: "jest-environment-jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  // Frontend tests live under tests/ (backend tests use pytest, not Jest).
  testMatch: ["<rootDir>/tests/**/*.test.{ts,tsx}"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
  collectCoverageFrom: [
    "lib/**/*.{ts,tsx}",
    "components/**/*.{ts,tsx}",
    "!**/*.d.ts",
  ],
}

export default createJestConfig(config)

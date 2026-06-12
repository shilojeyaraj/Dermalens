/**
 * End-to-end test STUB for the core scan -> analysis -> recommendations flow.
 *
 * This is intentionally skipped: a real run needs the Next.js app + the backend
 * API (apps/api) running, plus Playwright installed and browsers downloaded.
 * It documents the intended e2e coverage and is wired so CI never fails on it.
 *
 * To enable:
 *   1. npm i -D @playwright/test && npx playwright install --with-deps
 *   2. Start the app:  npm run dev   (and the backend, or point at a deployed URL)
 *   3. Replace this stub's body and run:  npx playwright test
 */

// Minimal local shims so this file type-checks without @playwright/test installed.
type TestFn = ((name: string, fn: () => Promise<void> | void) => void) & {
  skip: (name: string, fn: () => Promise<void> | void) => void
}
const test: TestFn = (() => {}) as TestFn
test.skip = () => {}

test.skip("user can scan a face photo and receive product recommendations", async () => {
  // 1. Navigate to /scan
  // 2. Upload/capture a face image
  // 3. Submit for analysis and wait for the results view
  // 4. Assert a skin-condition summary and at least one recommended product render
  // 5. Navigate to /products and assert the recommendations persist
})

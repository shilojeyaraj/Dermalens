import { cn } from "@/lib/utils"

/**
 * Unit tests for the `cn` class-name helper (clsx + tailwind-merge).
 * This utility is used by nearly every UI component, so its behavior matters.
 */
describe("cn", () => {
  it("joins multiple class names", () => {
    expect(cn("a", "b", "c")).toBe("a b c")
  })

  it("drops falsy values (false, null, undefined, empty string)", () => {
    expect(cn("base", false, null, undefined, "", "active")).toBe("base active")
  })

  it("merges conflicting Tailwind utilities so the last one wins", () => {
    // tailwind-merge resolves px-2 vs px-4 to a single, last-wins value
    expect(cn("px-2", "px-4")).toBe("px-4")
    expect(cn("text-sm", "text-lg")).toBe("text-lg")
  })

  it("supports conditional object syntax from clsx", () => {
    expect(cn("btn", { "btn-active": true, "btn-disabled": false })).toBe("btn btn-active")
  })

  it("flattens arrays of class names", () => {
    expect(cn(["flex", "items-center"], "gap-2")).toBe("flex items-center gap-2")
  })
})

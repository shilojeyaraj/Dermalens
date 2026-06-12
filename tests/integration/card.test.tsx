import { render, screen } from "@testing-library/react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

/**
 * Integration test: renders the composed shadcn/ui Card primitives together and
 * asserts the full subtree mounts and displays its content. Exercises the real
 * components + the `cn` helper through React Testing Library + jsdom.
 */
describe("Card", () => {
  it("renders a composed card with header, title, description, and content", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Skin Analysis</CardTitle>
          <CardDescription>Your latest results</CardDescription>
        </CardHeader>
        <CardContent>Hydration: 72%</CardContent>
      </Card>
    )

    expect(screen.getByText("Skin Analysis")).toBeInTheDocument()
    expect(screen.getByText("Your latest results")).toBeInTheDocument()
    expect(screen.getByText("Hydration: 72%")).toBeInTheDocument()
  })

  it("forwards custom className onto the card root", () => {
    render(
      <Card className="custom-card" data-testid="card">
        <CardContent>Body</CardContent>
      </Card>
    )

    expect(screen.getByTestId("card")).toHaveClass("custom-card")
  })
})

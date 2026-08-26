import type { Plugin } from "@opencode-ai/plugin"

// Post-build verifier reminder plugin.
// After any Bash tool call that looks like an AL build/compile,
// append a reminder to run the four mandatory verifier agents.

const BUILD_PATTERNS = [
  /Run-AlPipeline/i,
  /Compile-AppInContainer/i,
  /Compile-App(?:[^a-zA-Z]|$)/i,
  /(?:^|[^a-zA-Z])alc(?:\.exe)?(?:[^a-zA-Z]|$)/i,
]

function looksLikeBuild(cmd: string): boolean {
  return BUILD_PATTERNS.some((re) => re.test(cmd))
}

export default (async () => {
  return {
    "tool.execute.after": async (
      input: { tool: string; args: Record<string, unknown> },
      output: { result: unknown }
    ) => {
      if (input.tool !== "bash") return

      const cmd =
        typeof input.args?.command === "string" ? input.args.command : ""
      if (!looksLikeBuild(cmd)) return

      const reminder = [
        "",
        "A Business Central build/compile just ran.",
        "Per repo policy (AGENTS.md), before treating this feature's Implement step",
        "complete you MUST:",
        "",
        "  1. Run the mandatory verifier agents IN PARALLEL:",
        "     al-code-quality-reviewer, al-readability-checker.",
        "     Tests are opt-in (AGENTS.md Testing policy): only if tests were",
        "     opted in for this feature, also run al-test-coverage-validator and",
        "     al-test-validator. Otherwise skip them and do not treat a missing",
        "     test as a finding.",
        "  2. Apply the house rules and the AL style guide:",
        "     .opencode/skills/al-code-review/SKILL.md and",
        "     .opencode/skills/al-code-review/styleguide.md.",
        "     Read them, do not review from memory. House rules outrank BCQuality.",
        "     Cite style guide findings as house:styleguide-<section>-<slug> with",
        "     references[] naming styleguide.md and the section.",
        "  3. Run a BCQuality review over the changed AL: consume .opencode/bcquality",
        "     (al-code-review skill), citing matched knowledge files in each",
        "     finding's references[].",
        "",
        "Do not consider the task done until these have run and their findings are",
        "resolved or explicitly acknowledged.",
        "",
      ].join("\n")

      // Append the reminder to the tool output so the model sees it.
      if (typeof output.result === "string") {
        ;(output as { result: unknown }).result = output.result + reminder
      } else if (
        output.result &&
        typeof output.result === "object" &&
        "content" in output.result &&
        typeof (output.result as { content: unknown }).content === "string"
      ) {
        ;(output.result as { content: string }).content += reminder
      }
    },
  }
}) satisfies Plugin

import type { Plugin } from "@opencode-ai/plugin"

// Post-build verifier reminder plugin.
// Bash is the only tool whose command and exit result this hook can inspect.

const BUILD_PATTERNS = [
  /(?:^|[\n;&|])\s*(?:pwsh\s+(?:-\S+\s+)*)?(?:\S*\/)?(?:Run-AlPipeline|Compile-AppInContainer|Compile-App)(?:\.ps1)?(?:\s|$)/im,
  /(?:^|[\n;&|])\s*(?:time\s+)?(?:"?\$ALC"?|"?(?:[^"\s]*\/)?alc(?:\.exe)?"?)\s+(?:\\\s*)?\/project:/im,
]

function looksLikeBuild(cmd: string): boolean {
  return BUILD_PATTERNS.some((re) => re.test(cmd))
}

type ToolOutput = {
  title: string
  output: string
  metadata: unknown
}

function metadataExitCode(metadata: unknown): number | undefined {
  if (!metadata || typeof metadata !== "object") return undefined

  const value = metadata as Record<string, unknown>
  for (const key of ["exit", "exitCode", "exit_code"]) {
    if (typeof value[key] === "number") return value[key]
  }

  if (value.structured && typeof value.structured === "object") {
    return metadataExitCode(value.structured)
  }

  return undefined
}

function metadataTimedOut(metadata: unknown): boolean {
  if (!metadata || typeof metadata !== "object") return false

  const value = metadata as Record<string, unknown>
  if (value.timeout === true || value.timedOut === true) return true
  return metadataTimedOut(value.structured)
}

function buildSucceeded(output: ToolOutput): boolean {
  if (metadataTimedOut(output.metadata)) return false

  if (
    /\b(?:CompilationFailed|BUILD FAILED|Compilation failed|Build failed)\b/i.test(
      output.output
    ) ||
    /(?:error|fatal)[^\n]*(?:compile|compilation|build)/i.test(output.output)
  ) {
    return false
  }

  const reportedExitMatch = output.output.match(/^exit=(-?\d+)$/im)
  if (reportedExitMatch) return Number(reportedExitMatch[1]) === 0

  const exitMatch = output.output.match(/Command exited with code\s+(-?\d+)/i)
  if (exitMatch) return Number(exitMatch[1]) === 0

  const exitCode = metadataExitCode(output.metadata)
  if (exitCode !== undefined) return exitCode === 0

  return /\b(?:Build succeeded|Compilation succeeded|package (?:was )?created successfully)\b/i.test(
    output.output
  )
}

export default (async () => {
  return {
    "tool.execute.after": async (
      input: { tool: string; args: Record<string, unknown> },
      output: ToolOutput
    ) => {
      if (input.tool !== "bash") return

      const cmd =
        typeof input.args?.command === "string" ? input.args.command : ""
      if (!looksLikeBuild(cmd)) return
      if (!buildSucceeded(output)) return

      const reminder = [
        "",
        "A successful Business Central build/compile was detected in Bash.",
        "Per repo policy (AGENTS.md), before treating this feature's Test step",
        "complete you MUST:",
        "",
        "  1. Run the mandatory verifier agents IN PARALLEL:",
        "     al-code-quality-reviewer, al-readability-checker.",
        "     Tests are opt-in (.opencode/skills/sdd/SKILL.md): only if tests were",
        "     opted in for this feature, also run al-test-coverage-validator and",
        "     al-test-validator. Otherwise skip them and do not treat a missing",
        "     test as a finding.",
        "  2. Apply the house rules and the AL style guide:",
        "     .opencode/skills/al-code-review/SKILL.md and",
        "     .opencode/skills/al-code-review/styleguide.md.",
        "     Read them, do not review from memory. House rules outrank BCQuality.",
        "     Emit overlay-only house findings in the separate local reviewer",
        "     shape; do not put scaffold paths in BCQuality DO references.",
        "  3. Run the BCQuality action-skill flow over the changed AL. Start at",
        "     .opencode/BCQuality-ADIGO/skills/entry.md, follow READ and DO, and",
        "     emit the selected action skill's findings report.",
        "",
        "Do not consider the task done until these have run and their findings are",
        "resolved or explicitly acknowledged.",
        "",
      ].join("\n")

      output.output += reminder
    },
  }
}) satisfies Plugin

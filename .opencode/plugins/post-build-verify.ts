import type { Plugin } from "@opencode-ai/plugin"

// Post-build verifier reminder plugin.
// Bash is the only tool whose command and exit result this hook can inspect.

const BUILD_PATTERNS = [
  /(?:^|[\n;&|])\s*(?:pwsh\s+(?:-\S+\s+)*)?(?:\S*\/)?(?:Run-AlPipeline|Compile-AppInContainer|Compile-App)(?:\.ps1)?(?:\s|$)/im,
  /(?:^|[\n;&|])\s*(?:time\s+)?(?:"?\$ALC"?|"?(?:[^"\s]*\/)?alc(?:\.exe)?"?)\s+(?:\\\s*)?\/project:/im,
]

export function looksLikeBuild(cmd: string): boolean {
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

export function buildSucceeded(output: ToolOutput): boolean {
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
        "  1. If Automated tests=yes, dispatch al-test-runner now, before test",
        "     coverage or quality validation. Any failed count, runner failure or",
        "     partial result, or unexecuted required test blocks Test. Fix and rerun",
        "     the full required selection. If tests=no, skip the runner.",
        "  2. Run the exact applicable verifier set IN PARALLEL:",
        "     always al-code-quality-reviewer and al-readability-checker; when",
        "     tests=yes also al-test-coverage-validator and al-test-validator; when",
        "     integration is touched also al-integration-pattern-reviewer,",
        "     azure-integration-validator, and al-event-subscriber-auditor.",
        "     Resolve findings or record a durable approved waiver with explicit",
        "     owner and date, then rerun this exact applicable set. Acknowledgement",
        "     alone is not resolution.",
        "     Each verifier owns its exact tools/route_entry.py requested-skill-id and",
        "     routed READ/DO execution; do not run an unspecified or fuzzy action.",
        "  3. Apply the house rules and the AL style guide:",
        "     .opencode/skills/al-code-review/SKILL.md and",
        "     .opencode/skills/al-code-review/styleguide.md.",
        "     Read them, do not review from memory. House rules outrank BCQuality.",
        "     Emit overlay-only house findings in the separate local reviewer",
        "     shape; do not put scaffold paths in BCQuality DO references.",
        "",
        "If any Test fix changes production behavior, rerun the Opus semantic",
        "implementation gate, resolve findings, and rerun it to outcome pass.",
        "Record the initial semantic gate, compile/baseline evidence, test",
        "execution, both verifier runs, semantic reruns, waivers, and the executed",
        "client result in validation.md. Preserve the runner BCQuality outcome and",
        "summary.execution.status verbatim.",
        "",
      ].join("\n")

      output.output += reminder
    },
  }
}) satisfies Plugin

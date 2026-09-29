import type { Plugin } from "@opencode-ai/plugin"

// Post-build verifier reminder plugin.
// Bash is the only tool whose command and exit result this hook can inspect.

const BUILD_PATTERNS = [
  /(?:^|[\n;&|])\s*(?:time\s+)?(?:bash\s+)?(?:"[^"\n]*\/al-compile\/scripts\/compile\.sh"|'[^'\n]*\/al-compile\/scripts\/compile\.sh'|[^\s"']*\/al-compile\/scripts\/compile\.sh)(?=\s|$)/im,
  /(?:^|[\n;&|])\s*(?:time\s+)?dotnet\s+(?:"[^"\n]*\balc\.dll"|'[^'\n]*\balc\.dll'|\S*\balc\.dll)\s+(?:\\\s*)?\/project:/im,
  /(?:^|[\n;&|])\s*(?:pwsh\s+(?:-\S+\s+)*)?(?:\S*\/)?(?:Run-AlPipeline|Compile-AppInContainer|Compile-App)(?:\.ps1)?(?:\s|$)/im,
  /(?:^|[\n;&|])\s*(?:time\s+)?(?:"?\$ALC"?|"?(?:[^"\s]*\/)?alc(?:\.exe)?"?)\s+(?:\\\s*)?\/project:/im,
]

function commandSegments(cmd: string): string[] {
  const segments: string[] = []
  let start = 0
  let quote = ""
  let escaped = false
  for (let i = 0; i < cmd.length; i++) {
    const char = cmd[i]
    if (escaped) { escaped = false; continue }
    if (char === "\\" && quote !== "'") { escaped = true; continue }
    if (quote) {
      if (char === quote) quote = ""
    } else if (char === '"' || char === "'" || char === "`") {
      quote = char
    } else if ("\n;&|".includes(char)) {
      segments.push(cmd.slice(start, i))
      start = i + 1
    }
  }
  segments.push(cmd.slice(start))
  return segments.map((segment) => segment.trim()).filter(Boolean)
}

export function looksLikeBuild(cmd: string): boolean {
  // Match only the beginning of a shell segment, not separators inside quotes.
  return commandSegments(cmd).some((segment) =>
    BUILD_PATTERNS.some((re) => re.exec(segment)?.index === 0)
  )
}

type ToolOutput = {
  title: string
  output: string
  metadata: unknown
}

function metadataExitCodes(metadata: unknown): number[] {
  if (!metadata || typeof metadata !== "object") return []

  const value = metadata as Record<string, unknown>
  return ["exit", "exitCode", "exit_code"].flatMap((key) =>
    typeof value[key] === "number" ? [value[key] as number] : []
  ).concat(metadataExitCodes(value.structured))
}

function metadataTimedOut(metadata: unknown): boolean {
  if (!metadata || typeof metadata !== "object") return false

  const value = metadata as Record<string, unknown>
  if (value.timeout === true || value.timedOut === true) return true
  return metadataTimedOut(value.structured)
}

export function buildSucceeded(output: ToolOutput, allowExitOnly = true): boolean {
  if (metadataTimedOut(output.metadata)) return false

  if (
    /\b(?:CompilationFailed|BUILD FAILED|Compilation failed|Build failed)\b/i.test(
      output.output
    ) ||
    /(?:error|fatal)[^\n]*(?:compile|compilation|build)/i.test(output.output) ||
    /^(?:Command|Process|Build|Compilation)\s+(?:timed out|timeout|(?:was )?(?:terminated|aborted))\b/im.test(output.output) ||
    /:\s*(?:error|fatal)\b/i.test(output.output)
  ) {
    return false
  }

  const summaries = [...output.output.matchAll(/^exit=(-?\d+)(?: errors=(\d+) warnings=(\d+) infos=(\d+))?\s*$/gim)]
  if (summaries.some((match) => Number(match[1]) !== 0 || Number(match[2] ?? 0) !== 0)) return false
  const exitCodes = metadataExitCodes(output.metadata).concat(
    [...output.output.matchAll(/Command exited with code\s+(-?\d+)/gi)].map((match) => Number(match[1]))
  )
  // Failure evidence always wins, including conflicting nested metadata.
  if (exitCodes.some((code) => code !== 0)) return false
  if (summaries.length || (allowExitOnly && exitCodes.length)) return true

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
      // A compound shell's exit status can belong to a different or skipped
      // command. Require actual build output, especially the wrapper summary.
      const singleCommand = commandSegments(cmd).length === 1
      if (!buildSucceeded(output, singleCommand)) return

      const reminder = [
        "",
        "A successful Business Central build/compile was detected in Bash.",
        "Classify compile diagnostics against the baseline; exit=0 alone is not a clean build.",
        "Follow AGENTS.md and the house review/style rules. Run the applicable verifiers",
        "in parallel: always al-code-quality-reviewer and al-readability-checker.",
        "Add specialists independently: al-integration-pattern-reviewer for changed actual",
        "BC external flows; azure-integration-validator for changed Azure artifacts;",
        "al-event-subscriber-auditor for changed subscribers or affected publisher signatures.",
        "One complete clean finding-free pass suffices on unchanged review inputs.",
        "Resolve findings or record explicitly approved waivers with owner and date.",
        "Fixes, waivers, or relevant input changes require confirmation by the exact",
        "applicable verifier set, retaining existing triggers and adding new ones.",
        "Partial/API-failed reviews never pass; acknowledgement is not resolution or waiver.",
        "In SDD only, follow the sdd Test step: if Automated tests=yes, dispatch",
        "al-test-runner before al-test-coverage-validator and al-test-validator; failed,",
        "partial, or unexecuted required tests block Test. Rerun the semantic implementation",
        "gate after behavior-changing Test fixes and record evidence in validation.md per sdd.",
        "Outside SDD, follow AGENTS.md's quick-fix review path.",
        "Coordinator: follow hunk-review to publish useful German notes to the matching",
        "live diff, refresh after fixes, and verify publication and note visibility.",
        "",
      ].join("\n")

      output.output += reminder
    },
  }
}) satisfies Plugin

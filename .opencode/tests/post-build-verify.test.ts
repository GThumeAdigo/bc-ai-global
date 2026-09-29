import assert from "node:assert/strict"
import test from "node:test"
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { fileURLToPath } from "node:url"
import { spawnSync } from "node:child_process"

import postBuildVerify, { buildSucceeded, looksLikeBuild } from "../plugins/post-build-verify.ts"

test("recognizes supported AL compile commands", () => {
  assert.equal(looksLikeBuild('"$ALC" /project:"/tmp/app"'), true)
  for (const command of [
    'bash .opencode/skills/al-compile/scripts/compile.sh App',
    '.opencode/skills/al-compile/scripts/compile.sh App',
    'bash "/tmp/shared scaffold/.opencode/skills/al-compile/scripts/compile.sh" "My App"',
    "'/tmp/shared scaffold/.opencode/skills/al-compile/scripts/compile.sh' App",
    'dotnet "/tmp/AL extension/alc.dll" /project:App',
  ]) assert.equal(looksLikeBuild(command), true, command)
  assert.equal(looksLikeBuild("npm test"), false)
  assert.equal(looksLikeBuild("cat .opencode/skills/al-compile/scripts/compile.sh"), false)
  assert.equal(looksLikeBuild("echo bash .opencode/skills/al-compile/scripts/compile.sh App"), false)
  assert.equal(looksLikeBuild('echo "example; bash .opencode/skills/al-compile/scripts/compile.sh App"'), false)
  assert.equal(looksLikeBuild("echo 'example; bash .opencode/skills/al-compile/scripts/compile.sh App'"), false)
  assert.equal(looksLikeBuild('echo "example\\\"; bash .opencode/skills/al-compile/scripts/compile.sh App"'), false)
})

test("requires successful build evidence", () => {
  assert.equal(
    buildSucceeded({ title: "compile", output: "Build succeeded", metadata: {} }),
    true
  )
  assert.equal(
    buildSucceeded({ title: "compile", output: "Build failed", metadata: { exitCode: 1 } }),
    false
  )
})

test("successful compile appends the concise scope-aware policy reminder", async () => {
  const hooks = await postBuildVerify()
  const output = { title: "compile", output: "Build succeeded", metadata: { exitCode: 0 } }

  await hooks["tool.execute.after"]?.(
    { tool: "bash", args: { command: '"$ALC" /project:"/tmp/app"' } } as never,
    output as never
  )

  assert.match(output.output, /dispatch\s+al-test-runner/)
  assert.match(output.output, /One complete clean finding-free pass suffices on unchanged review inputs/)
  assert.match(output.output, /confirmation by the exact\s+applicable verifier set/)
  assert.match(output.output, /retaining existing triggers and adding new ones/)
  assert.match(output.output, /Add specialists independently/)
  assert.match(output.output, /BC external flows; azure-integration-validator for changed Azure artifacts/)
  assert.match(output.output, /changed subscribers or affected publisher signatures/)
  assert.match(output.output, /Partial\/API-failed reviews never pass/)
  assert.match(output.output, /acknowledgement is not resolution or waiver/)
  assert.match(output.output, /In SDD only,[\s\S]*Rerun the semantic implementation[\s\S]*validation\.md per sdd/)
  assert.match(output.output, /Outside SDD, follow AGENTS\.md's quick-fix review path/)
  assert.match(output.output, /Coordinator: follow hunk-review to publish useful German notes/)
  assert.match(output.output, /verify publication and note visibility/)
  assert.doesNotMatch(output.output, /both verifier runs|integration is touched/)
})

test("failed compile does not append the reminder", async () => {
  const hooks = await postBuildVerify()
  const output = { title: "compile", output: "Build failed", metadata: { exitCode: 1 } }

  await hooks["tool.execute.after"]?.(
    { tool: "bash", args: { command: '"$ALC" /project:"/tmp/app"' } } as never,
    output as never
  )

  assert.equal(output.output, "Build failed")
})

test("wrapper summaries cannot override failure or timeout evidence", async () => {
  const summary = "exit=0 errors=0 warnings=2 infos=1"
  assert.equal(buildSucceeded({ title: "", output: summary, metadata: {} }), true)
  assert.equal(buildSucceeded({ title: "", output: "app: /work/timeout/App\n" + summary, metadata: {} }), true)
  const cases = [
    { output: summary, metadata: { exitCode: 1 } },
    { output: summary, metadata: { exit: 0, exitCode: 1 } },
    { output: summary, metadata: { exit: 0, structured: { exit_code: 2 } } },
    { output: summary, metadata: { timedOut: true, exit: 0 } },
    { output: summary, metadata: { structured: { timeout: true } } },
    { output: summary + "\nCommand exited with code 1", metadata: {} },
    { output: summary + "\nCommand timed out", metadata: {} },
    { output: "exit=1 errors=0 warnings=0 infos=0", metadata: { exit: 0 } },
    { output: "exit=0 errors=1 warnings=0 infos=0", metadata: { exit: 0 } },
    { output: "exit=1\n" + summary, metadata: {} },
  ]
  const hooks = await postBuildVerify()
  for (const fixture of cases) {
    const output = { title: "compile", ...fixture }
    assert.equal(buildSucceeded(output), false, JSON.stringify(fixture))
    await hooks["tool.execute.after"]?.(
      { tool: "bash", args: { command: "bash .opencode/skills/al-compile/scripts/compile.sh App" } } as never,
      output as never
    )
    assert.equal(output.output, fixture.output)
  }
})

test("quoted examples and skipped builds do not produce reminders", async () => {
  const hooks = await postBuildVerify()
  for (const command of [
    'echo "example; bash .opencode/skills/al-compile/scripts/compile.sh App"',
    'true || bash .opencode/skills/al-compile/scripts/compile.sh App',
    'false && bash .opencode/skills/al-compile/scripts/compile.sh App; true',
  ]) {
    const output = { title: "shell", output: "", metadata: { exitCode: 0 } }
    await hooks["tool.execute.after"]?.(
      { tool: "bash", args: { command } } as never, output as never
    )
    assert.equal(output.output, "", command)
  }
  const output = { title: "compile", output: "exit=0 errors=0 warnings=0 infos=0", metadata: { exitCode: 0 } }
  await hooks["tool.execute.after"]?.(
    { tool: "bash", args: { command: 'true && bash .opencode/skills/al-compile/scripts/compile.sh App' } } as never,
    output as never
  )
  assert.match(output.output, /One complete clean finding-free pass/)
})

test("real compile wrapper output reaches the hook on success only", async () => {
  const root = mkdtempSync(join(tmpdir(), "post-build-fixture-"))
  const wrapper = fileURLToPath(new URL("../skills/al-compile/scripts/compile.sh", import.meta.url))
  const app = join(root, "My App")
  const bin = join(root, ".vscode/extensions/ms-dynamics-smb.al-1.0/bin")
  const logs: string[] = []
  try {
    mkdirSync(app, { recursive: true })
    mkdirSync(join(bin, "linux"), { recursive: true })
    mkdirSync(join(bin, "Analyzers"))
    writeFileSync(join(app, "app.json"), "{}")
    const ruleset = join(root, "ruleset.json")
    writeFileSync(ruleset, "{}")
    const analyzers = [
      ...["CodeCop", "UICop", "PerTenantExtensionCop"].map((name) => `Microsoft.Dynamics.Nav.${name}.dll`),
      ...["ApplicationCop", "DocumentationCop", "FormattingCop", "LinterCop", "PlatformCop", "TestAutomationCop", "Common"].map((name) => `ALCops.${name}.dll`),
    ]
    for (const name of analyzers) writeFileSync(join(bin, "Analyzers", name), "")
    writeFileSync(join(bin, "linux/alc"), '#!/usr/bin/env bash\nexit "$FAKE_EXIT"\n', { mode: 0o755 })
    const hooks = await postBuildVerify()
    for (const exit of [0, 1]) {
      const result = spawnSync("bash", [wrapper, app, ruleset], {
        env: { ...process.env, HOME: root, FAKE_EXIT: String(exit) }, encoding: "utf8",
      })
      const log = result.stdout.match(/^log:\s+(\/tmp\/alcompile\.[^\n]+)\/compile\.log$/m)
      if (log) logs.push(log[1])
      assert.equal(result.status, exit, result.stderr)
      assert.match(result.stdout, new RegExp(`exit=${exit} errors=0 warnings=0 infos=0`))
      const output = { title: "compile", output: result.stdout, metadata: {} }
      await hooks["tool.execute.after"]?.(
        { tool: "bash", args: { command: `bash "${wrapper}" "${app}" "${ruleset}"` } } as never,
        output as never
      )
      assert.equal(output.output.includes("One complete clean finding-free pass"), exit === 0)
    }
  } finally {
    for (const log of logs) rmSync(log, { recursive: true, force: true })
    rmSync(root, { recursive: true, force: true })
  }
})

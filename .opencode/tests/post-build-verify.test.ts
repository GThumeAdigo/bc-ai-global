import assert from "node:assert/strict"
import test from "node:test"

import postBuildVerify, { buildSucceeded, looksLikeBuild } from "../plugins/post-build-verify.ts"

test("recognizes supported AL compile commands", () => {
  assert.equal(looksLikeBuild('"$ALC" /project:"/tmp/app"'), true)
  assert.equal(looksLikeBuild("npm test"), false)
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

test("successful compile appends the complete Test reminder", async () => {
  const hooks = await postBuildVerify()
  const output = { title: "compile", output: "Build succeeded", metadata: { exitCode: 0 } }

  await hooks["tool.execute.after"]?.(
    { tool: "bash", args: { command: '"$ALC" /project:"/tmp/app"' } } as never,
    output as never
  )

  assert.match(output.output, /dispatch al-test-runner/)
  assert.match(output.output, /rerun this exact applicable set/)
  assert.match(output.output, /integration is touched/)
  assert.match(output.output, /Acknowledgement\s+alone is not resolution/)
  assert.match(output.output, /tools\/route_entry\.py requested-skill-id/)
  assert.match(output.output, /routed READ\/DO execution/)
  assert.match(output.output, /rerun the Opus semantic/)
  assert.match(output.output, /summary\.execution\.status verbatim/)
  assert.doesNotMatch(output.output, /Run the BCQuality action-skill flow/)
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

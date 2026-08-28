# App Context: <App Name>

> This file belongs to this AL app checkout. It is copied by `init-linux.sh`,
> never symlinked, and is the app-specific companion to the shared `AGENTS.md`.
> Fill it in before feature work. Keep durable product decisions in `specs/`.

## App identity

- App name: TODO
- Publisher: TODO
- Version / target BC version: TODO
- Primary app folder: TODO
- Related workspace apps and dependency order: TODO

## AL conventions

- Namespace root: TODO
- Object prefix: TODO
- Object ID range: TODO
- Error handling codeunit / pattern: TODO
- App-specific analyzer rules or exceptions: TODO

## Architecture and integrations

- Foundation apps and key dependencies: TODO
- External integrations and authentication boundaries: TODO
- Data ownership and sensitive data constraints: TODO
- Supported localisations and tenant assumptions: TODO

## Deployment and compatibility

- Deployment status: unreleased | sandbox | production
- Production/persisted-data compatibility required: yes | no
- Trusted released baseline ref: TODO | not-applicable

The explicit compatibility decision controls upgrade and obsolete review. A
release tag or branch name alone never changes `no` to `yes`. When compatibility
is `yes`, the trusted baseline must identify the released source or package to
compare; without it, compatibility review is partial.

## Verification environment

- Compile/build command and known baseline findings: TODO
- Sandbox URL and publishing prerequisites: TODO
- Web-client verification prerequisites: TODO

## Local navigation

- Important source folders or objects: TODO
- App-specific documentation: TODO
- App-specific agent memories or tooling notes: TODO

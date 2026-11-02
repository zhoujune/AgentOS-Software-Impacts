# AgentOS-RK source release scope and dependency record

This document describes the proposed source-only release and supersedes older release-status statements where they conflict. The history documents describe earlier candidate decisions and are retained as records, not current release status.

## Distribution scope

The project owner confirmed on 2026-11-02 that they had reviewed and can authorize redistribution of the candidate source, patches, fixtures, figures and relevant upstream artifacts, including contributor and institutional rights. First-party software is distributed under the top-level MIT license. Third-party components retain their own terms; this confirmation does not replace third-party license requirements. No model weights, guest kernel or root filesystem images, QEMU binaries, or third-party JAR are included in this companion source tree. Do not interpret its MIT notice as a grant over those independently licensed dependencies.

## Reproduction inputs and limits

The replay script fetches `https://github.com/zhoujune/AgentOS` at commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`, applies three patches, copies four overlay scripts, and checks the seven companion inputs against recorded hashes. The upstream checkout includes a prebuilt guest image used in replay. This source archive alone is therefore not a self-contained executable capsule; users obtain upstream artifacts separately. The upstream project and any binary distributors remain responsible for applicable component notices and source obligations. This document does not certify binary redistribution compliance.

The replay requires an x86-64 Linux host with Git, Python 3, QEMU x86-64, e2fsprogs and SHA-256 utilities. The recorded CI installed QEMU through Ubuntu packages; system package versions may change. An optional full guest rebuild requires Buildroot; the exact Buildroot commit and a complete target-package/version/license lock are not established. Buildroot 2026.02 and Linux 6.12.47 are recorded in prior environment notes, but these descriptions do not establish a reproducible full build. Generate and review Buildroot `make legal-info` output and the actual sources, configuration and package licenses before separately distributing guest binaries.

The 216-episode local-model study additionally depends on model services and separately governed weights; weights are not distributed here. The 90-case memory study uses deterministic CPU-only replays. Neither result establishes independent adoption. A non-maintainer reproduction remains future work.

## Evidence

The earlier consolidated candidate at commit `380940e751ae40a1658cf7612f3391c914464f11` passed clean-host technical reproduction in [GitHub Actions run 41393152866](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41393152866). Check CI against the actual released commit before citing release validation. A source archive should be matched to the final Git tree and a version-specific archive record; do not describe it as a binary capsule.

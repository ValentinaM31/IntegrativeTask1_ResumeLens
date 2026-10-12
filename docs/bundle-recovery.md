# Disk export protection and recovery

`save_bundle(result, destination, force=False)` keeps its public signature and
returns the destination `Path` after success. The four filenames, UTF-8/LF payloads,
processing decisions and JSON 1.0 contract are unchanged. The browser ZIP is built
in memory and does not create this disk workspace.

## Export sequence

1. Validate all stages against the original source and preflight all four target
   filenames. Existing outputs require `force=True`; directories and symbolic
   links at output filenames are rejected even with force. Validation failure does
   not create the destination. Unrelated files remain untouched.
2. Exclusively create `destination/.resumelens-export.lock/` and repeat the target
   preflight. A pre-existing workspace, including a regular file with that name,
   blocks another exporter without deleting its contents.
3. Write, flush and close all four new outputs in `prepared/`. Copy each existing
   original as bytes into `previous/`, and preserve supported original mode bits
   on the prepared replacement. An error at this stage leaves final reports
   unchanged.
4. Record the original-presence list in `recovery.json` with phase `prepared`.
   Metadata updates themselves use a temporary file and individual replacement.
   Only after every backup and this record are complete does publication start.
5. Reserve originally absent filenames using exclusive binary creation. Replace
   each final report from `prepared/` using `os.replace`. Record phase `committed`
   after all four replacements finish.
6. Remove the private workspace after successful publication or successful
   rollback. An empty destination directory can remain after a failed first
   export; generated report placeholders are removed during successful recovery.

The workspace is in the destination filesystem, so prepared files, backups and
their replacements share that filesystem. Exclusive ownership coordinates
exporters using this function; it does not lock readers or unrelated editors.
Supported mode bits and modification timestamps are copied during restoration;
ownership, ACLs and hard-link identity are not preservation guarantees. Read-only
private copies can have their write bit enabled during cleanup on Windows; that
cleanup does not change the originals' permissions.

## Controlled failures

On a publication failure, the saver restores every touched originally present
report from its backup and removes touched reports that were originally absent.
It restores in reverse order and attempts the other files if one restoration
fails. Every backup is retained until the entire recovery succeeds. A failure
while recording `committed`, after all four replacements, also triggers rollback.
Caught interruptions such as `KeyboardInterrupt` follow this same recovery path.

After successful rollback, the original exception is raised. The CLI handles
filesystem errors with exit code 2 and an English diagnostic. A subsequent export
can be retried after the filesystem issue is resolved.

If restoration is incomplete, `resumelens.workflow.BundleRecoveryError`, a subclass
of `OSError`, provides `recovery_directory` and `rollback_errors`. Its message
identifies affected filenames and the location of preserved originals. The
workspace remains and prevents another exporter from replacing the evidence
needed for recovery. Inspect both the exception's cause and the backup copies.

A cleanup-only error produces a `RuntimeWarning` with the workspace location. A
successfully published bundle still returns its destination; an export that
already failed still raises its original error. Cleanup failure does not imply
the reports were partially published. Inspect `recovery.json` before deciding
whether recovery or just cleanup is needed.

## Inspecting and recovering a retained workspace

First stop exporters using this destination and resolve the reported filesystem
problem, such as a file held open by another application. Do not delete the
workspace merely to make a retry possible.

The recovery record contains `version: 1`, `phase`, the fixed `bundle_files` list,
and `originals`, the subset present before publication. Its filenames must match
the four names in `resumelens.workflow.BUNDLE_FILES`; it does not contain arbitrary
paths or a copy of the input resume. Backup files themselves can contain candidate
information from the previous report. Keep them private while recovering.

For a controlled failure with a valid **prepared** record:

1. Verify that every name in `originals` has a complete regular-file backup in
   `previous/` before modifying any final report. If the record or backups are
   incomplete, inspect the files rather than guessing the previous state.
2. For each original, use `shutil.copy2` to copy `previous/<filename>` into a
   separate `prepared/<filename>.manual-restore` file, then `os.replace` that file
   onto the corresponding destination filename. Keep the backup until all files
   are restored. Avoid symlinks or directories introduced by outside programs.
3. Remove only the four named bundle outputs that are absent from `originals`.
   Retain unrelated files. Verify that each restored report's bytes match its
   backup and each originally absent report is absent again.
4. Remove the private workspace only after complete verification. Retry the
   normal CLI/API export. If an intermediate recovery step fails, keep the
   remaining backups and repeat recovery after resolving that error.

For a valid **committed** record after a controlled cleanup failure, all four new
outputs have already been published. Inspect their presence and contents, then
remove the leftover private workspace; do not restore old backups solely because
cleanup failed. The regression tests exercise recovery after an injected rollback
failure, verification of all original bytes, workspace cleanup and a fresh retry.

## Abrupt termination and other limits

This is not an atomic four-file or crash-durable filesystem transaction. Individual
replacements can be observed separately, and absent reports briefly have empty
reserved files. A killed process, power loss or abrupt system interruption can
leave old/new generations, placeholders or an incomplete preparation workspace.
The saver flushes new file contents but does not guarantee durable directory
metadata, durable original backups or automatic restart recovery. A missing or
malformed record after an abrupt interruption needs manual inspection.

Outside programs editing paths do not honor the workspace. Normal readers may
observe intermediate report generations. Controlled failure tests do not certify
behavior under disk corruption, every filesystem, power loss or forced process
termination. Native Windows verification remains necessary, particularly when
applications keep report files open or their permissions prevent replacement.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_bundle_recovery.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
```

Fifteen new test methods include partial writes, flush errors, backup/record
errors, all 16 combinations of original file presence with failures at each of
four promotion positions (64 subcases), sixteen successful partial-bundle
replacements, post-replacement exceptions, interruption, competing writers,
late collisions, incomplete rollback, cleanup warnings and the real CLI retry.
Originals deliberately include non-UTF-8 bytes and CRLF to verify byte preservation.
These are filesystem regressions, not independently collected resume evaluation.
See [verification results](test-results.md) for the current executed checks.

## Sources

- Python [os.replace and fsync](https://docs.python.org/3/library/os.html#os.replace).
- Python [exclusive file opening](https://docs.python.org/3/library/functions.html#open).
- Python [shutil.copy2 and rmtree](https://docs.python.org/3/library/shutil.html#shutil.copy2).

## Transient Windows file locks

Metadata publication, report replacement and restoration retry Windows permission/
sharing errors 5, 32 and 33 with a bounded backoff (six attempts, 0.58 seconds total
requested delay). Other errors are raised immediately. Persistent denial still
triggers the existing recovery path and retains backups if restoration fails.
This addresses observed intermittent replacement failures without weakening
filesystem permissions or claiming a transaction across all four files.

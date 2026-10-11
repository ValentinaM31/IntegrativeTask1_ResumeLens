"""Inject actual filesystem failures and verify prior report bytes survive."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import itertools
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
from threading import Event
import unittest
from unittest.mock import patch

from resumelens import process_complete_resume, save_bundle
from resumelens.workflow import (BUNDLE_FILES, BUNDLE_WORKSPACE, BundleRecoveryError,
                                 _bundle_payloads, _write_payload, _write_recovery_state)
from resumelens.workflow_cli import main


class BundleRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = process_complete_resume('Name: Ana María\nSkills: Python, SQL, ETL, Git.')
        cls.payloads = _bundle_payloads(cls.result)

    def seed(self, destination, present=BUNDLE_FILES):
        destination.mkdir(parents=True, exist_ok=True)
        for index, filename in enumerate(present):
            # Non-UTF-8 originals must be copied/restored as bytes, not decoded.
            (destination / filename).write_bytes(b'OLD\xff\r\n' + filename.encode('ascii'))
            os.utime(destination / filename, ns=(1600000000000000000 + index * 1000000000,) * 2)
        (destination / 'notes.txt').write_bytes(b'KEEP\r\n')
        return self.snapshot(destination)

    def snapshot(self, destination):
        return {item.name: item.read_bytes() for item in destination.iterdir() if item.is_file()}

    def assert_restored(self, destination, before):
        self.assertEqual(self.snapshot(destination), before)
        self.assertEqual(set(p.name for p in destination.iterdir()), set(before))

    def assert_saved(self, destination, payloads=None):
        expected = self.payloads if payloads is None else payloads
        for filename, content in expected.items():
            self.assertEqual((destination / filename).read_bytes(), content.encode('utf-8'))
        self.assertFalse((destination / BUNDLE_WORKSPACE).exists())

    def test_partial_staging_write_keeps_old_reports_and_cleans_new_destination(self):
        for present in (BUNDLE_FILES, ()):
            with self.subTest(present=present), tempfile.TemporaryDirectory() as folder:
                destination = Path(folder) / 'bundle'
                before = self.seed(destination, present)

                def fail(path, payload):
                    if path.name == 'classification.json':
                        with path.open('x', encoding='utf-8') as stream:
                            stream.write(payload[:20])
                        raise OSError('Injected disk-full error during a partial write')
                    return _write_payload(path, payload)

                with patch('resumelens.workflow._write_payload', side_effect=fail), self.assertRaises(OSError):
                    save_bundle(self.result, destination, force=True)
                self.assert_restored(destination, before)

    def test_fsync_failure_never_changes_existing_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)
            with patch('resumelens.workflow.os.fsync', side_effect=OSError('Injected flush failure')), self.assertRaises(OSError):
                save_bundle(self.result, destination, force=True)
            self.assert_restored(destination, before)

    def test_backup_failure_before_publication_keeps_all_originals(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)
            copy_file = shutil.copy2

            def fail(source, target, *args, **kwargs):
                if Path(target).parent.name == 'previous' and Path(target).name == 'classification.json':
                    Path(target).write_bytes(b'PARTIAL BACKUP')
                    raise OSError('Injected backup failure')
                return copy_file(source, target, *args, **kwargs)

            with patch('resumelens.workflow.shutil.copy2', side_effect=fail), self.assertRaises(OSError):
                save_bundle(self.result, destination, force=True)
            self.assert_restored(destination, before)

    def test_initial_recovery_record_failure_does_not_publish_any_report(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)
            with patch('resumelens.workflow._write_recovery_state', side_effect=OSError('Injected record failure')), self.assertRaises(OSError):
                save_bundle(self.result, destination, force=True)
            self.assert_restored(destination, before)

    def test_publication_failure_restores_all_file_presence_combinations(self):
        replace = os.replace
        for flags in itertools.product((False, True), repeat=4):
            present = tuple(name for name, exists in zip(BUNDLE_FILES, flags) if exists)
            for fail_index in range(4):
                with self.subTest(present=present, failure=fail_index), tempfile.TemporaryDirectory() as folder:
                    destination = Path(folder)
                    before = self.seed(destination, present)
                    timestamps = {name: (destination / name).stat().st_mtime_ns for name in present}
                    calls = 0

                    def fail(source, target):
                        nonlocal calls
                        if Path(source).parent.name == 'prepared' and Path(source).name in BUNDLE_FILES:
                            current = calls
                            calls += 1
                            if current == fail_index:
                                raise OSError('Injected intermediate replacement failure')
                        return replace(source, target)

                    with patch('resumelens.workflow.os.replace', side_effect=fail), self.assertRaises(OSError):
                        save_bundle(self.result, destination, force=True)
                    self.assert_restored(destination, before)
                    for name, timestamp in timestamps.items():
                        self.assertEqual((destination / name).stat().st_mtime_ns, timestamp)

    def test_success_replaces_all_partial_bundles_and_retains_unrelated_files(self):
        for flags in itertools.product((False, True), repeat=4):
            present = tuple(name for name, exists in zip(BUNDLE_FILES, flags) if exists)
            with self.subTest(present=present), tempfile.TemporaryDirectory() as folder:
                destination = Path(folder)
                self.seed(destination, present)
                modes = {name: stat.S_IMODE((destination / name).stat().st_mode) for name in present}
                self.assertEqual(save_bundle(self.result, destination, force=True), destination)
                self.assert_saved(destination)
                self.assertEqual((destination / 'notes.txt').read_bytes(), b'KEEP\r\n')
                self.assertEqual(set(p.name for p in destination.iterdir()), set(BUNDLE_FILES) | {'notes.txt'})
                for name, mode in modes.items():
                    self.assertEqual(stat.S_IMODE((destination / name).stat().st_mode), mode)

    def test_commit_record_failure_after_replacements_restores_old_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)

            def fail(workspace, originals, phase):
                if phase == 'committed':
                    raise OSError('Injected commit record failure')
                return _write_recovery_state(workspace, originals, phase)

            with patch('resumelens.workflow._write_recovery_state', side_effect=fail), self.assertRaises(OSError):
                save_bundle(self.result, destination, force=True)
            self.assert_restored(destination, before)

    def test_exception_after_a_replace_still_recovers_its_target(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)
            replace = os.replace

            def fail(source, target):
                replaced = replace(source, target)
                if Path(source).parent.name == 'prepared' and Path(source).name == 'classification.json':
                    raise OSError('Injected exception after replacement')
                return replaced

            with patch('resumelens.workflow.os.replace', side_effect=fail), self.assertRaises(OSError):
                save_bundle(self.result, destination, force=True)
            self.assert_restored(destination, before)

    def test_caught_keyboard_interrupt_during_publication_restores_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)
            replace = os.replace

            def interrupt(source, target):
                if Path(source).parent.name == 'prepared' and Path(source).name == 'classification.json':
                    raise KeyboardInterrupt()
                return replace(source, target)

            with patch('resumelens.workflow.os.replace', side_effect=interrupt), self.assertRaises(KeyboardInterrupt):
                save_bundle(self.result, destination, force=True)
            self.assert_restored(destination, before)

    def test_existing_workspace_is_preserved_and_blocks_another_export(self):
        for as_directory in (True, False):
            with self.subTest(directory=as_directory), tempfile.TemporaryDirectory() as folder:
                destination = Path(folder)
                before = self.seed(destination)
                workspace = destination / BUNDLE_WORKSPACE
                if as_directory:
                    workspace.mkdir()
                    (workspace / 'sentinel').write_bytes(b'KEEP RECOVERY')
                else:
                    workspace.write_bytes(b'KEEP RESERVED FILE')
                with self.assertRaisesRegex(FileExistsError, 'workspace already exists'):
                    save_bundle(self.result, destination, force=True)
                self.assertEqual({name: self.snapshot(destination)[name] for name in before}, before)
                self.assertEqual((workspace / 'sentinel' if as_directory else workspace).read_bytes(),
                                 b'KEEP RECOVERY' if as_directory else b'KEEP RESERVED FILE')

    def test_competing_writer_is_rejected_without_disturbing_the_owner(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)
            started, release = Event(), Event()

            def pause(path, payload):
                if path.parent.name == 'prepared' and path.name == 'first_stage.json':
                    started.set()
                    if not release.wait(10):
                        raise OSError('Timed out waiting for the controlled test release')
                return _write_payload(path, payload)

            with ThreadPoolExecutor(max_workers=1) as pool, patch('resumelens.workflow._write_payload', side_effect=pause):
                owner = pool.submit(save_bundle, self.result, destination, True)
                try:
                    self.assertTrue(started.wait(10))
                    with self.assertRaisesRegex(FileExistsError, 'workspace already exists'):
                        save_bundle(self.result, destination, force=True)
                    self.assertEqual(self.snapshot(destination), before)
                finally:
                    release.set()
                self.assertEqual(owner.result(timeout=10), destination)
            self.assert_saved(destination)

    def test_a_late_file_collision_is_not_overwritten_without_force(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination, ())

            def appear(workspace, originals, phase):
                _write_recovery_state(workspace, originals, phase)
                if phase == 'prepared':
                    (destination / 'candidate.html').write_bytes(b'NEW EXTERNAL FILE')

            with patch('resumelens.workflow._write_recovery_state', side_effect=appear), self.assertRaises(FileExistsError):
                save_bundle(self.result, destination)
            self.assert_restored(destination, {**before, 'candidate.html': b'NEW EXTERNAL FILE'})

    def test_failed_recovery_retains_complete_backups_and_allows_manual_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            before = self.seed(destination)
            replace = os.replace

            def fail(source, target):
                if Path(source).parent.name == 'prepared' and Path(source).name in ('classification.json', 'first_stage.json.restore'):
                    raise PermissionError('Injected inaccessible replacement')
                return replace(source, target)

            with patch('resumelens.workflow.os.replace', side_effect=fail):
                with self.assertRaises(BundleRecoveryError) as raised:
                    save_bundle(self.result, destination, force=True)
            recovery = raised.exception.recovery_directory
            self.assertEqual(recovery, destination / BUNDLE_WORKSPACE)
            self.assertIsInstance(raised.exception.__cause__, PermissionError)
            self.assertEqual(json.loads((recovery / 'recovery.json').read_text())['phase'], 'prepared')
            for filename in BUNDLE_FILES:
                self.assertEqual((recovery / 'previous' / filename).read_bytes(), before[filename])
            with self.assertRaises(FileExistsError):
                save_bundle(self.result, destination, force=True)
            # Reproduce the documented repair after the simulated OS error ends.
            for filename in BUNDLE_FILES:
                restored = recovery / 'prepared' / (filename + '.manual-restore')
                shutil.copy2(recovery / 'previous' / filename, restored)
                os.replace(restored, destination / filename)
            shutil.rmtree(recovery)
            self.assert_restored(destination, before)
            save_bundle(self.result, destination, force=True)
            self.assert_saved(destination)

    def test_cleanup_failure_is_reported_without_masking_the_export_outcome(self):
        for fail_export in (False, True):
            with self.subTest(failed_export=fail_export), tempfile.TemporaryDirectory() as folder:
                destination = Path(folder)
                before = self.seed(destination)
                replace = os.replace

                def fail(source, target):
                    if fail_export and Path(source).parent.name == 'prepared' and Path(source).name == 'classification.json':
                        raise OSError('Injected export failure')
                    return replace(source, target)

                with patch('resumelens.workflow._remove_workspace', side_effect=PermissionError('Injected cleanup failure')), \
                        patch('resumelens.workflow.os.replace', side_effect=fail), \
                        self.assertWarnsRegex(RuntimeWarning, 'Export cleanup failed'):
                    if fail_export:
                        with self.assertRaisesRegex(OSError, 'Injected export failure'):
                            save_bundle(self.result, destination, force=True)
                    else:
                        self.assertEqual(save_bundle(self.result, destination, force=True), destination)
                workspace = destination / BUNDLE_WORKSPACE
                state = json.loads((workspace / 'recovery.json').read_text())
                self.assertEqual(state['phase'], 'prepared' if fail_export else 'committed')
                if fail_export:
                    self.assertEqual(self.snapshot(destination), before)
                else:
                    for filename, content in self.payloads.items():
                        self.assertEqual((destination / filename).read_bytes(), content.encode('utf-8'))
                shutil.rmtree(workspace)

    def test_cli_reports_failure_preserves_reports_and_can_retry(self):
        for newline in ('\n', '\r\n'):
            with self.subTest(newline=repr(newline)), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                destination = root / 'bundle'
                before = self.seed(destination)
                source = root / 'resume.txt'
                text = self.result['source_text'].replace('\n', newline)
                # Binary creation prevents platform-dependent newline translation.
                source.write_bytes(text.encode('utf-8'))
                self.assertEqual(source.read_bytes(), text.encode('utf-8'))
                expected = _bundle_payloads(process_complete_resume(text))
                replace = os.replace

                def fail(source, target):
                    if Path(source).parent.name == 'prepared' and Path(source).name == 'classification.json':
                        raise OSError('Injected CLI export failure')
                    return replace(source, target)

                stdout, stderr = StringIO(), StringIO()
                with patch('resumelens.workflow.os.replace', side_effect=fail), redirect_stdout(stdout), redirect_stderr(stderr):
                    self.assertEqual(main([str(source), '-o', str(destination), '--force']), 2)
                self.assertEqual(stdout.getvalue(), '')
                self.assertIn('Error:', stderr.getvalue())
                self.assert_restored(destination, before)
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    self.assertEqual(main([str(source), '-o', str(destination), '--force']), 0)
                self.assert_saved(destination, expected)


if __name__ == '__main__':
    unittest.main()

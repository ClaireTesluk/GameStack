"""Test the exact publishing program embedded in the privileged workflow."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.safe_load((ROOT / '.github/workflows/tests.yml').read_text(encoding='utf-8'))
PUBLISH_STEP = next(s for s in WORKFLOW['jobs']['publish']['steps'] if s.get('id') == 'publish')
PUBLISHER = {'__name__': 'release_test'}
exec(compile(PUBLISH_STEP['run'], '<workflow-publisher>', 'exec'), PUBLISHER)
spec = importlib.util.spec_from_file_location('ci', ROOT / 'scripts/ci.py')
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


class ArtifactSmokeTests(unittest.TestCase):
    def test_workspace_retries_transient_windows_cleanup_failure(self):
        cleanup = tempfile.TemporaryDirectory.cleanup
        attempts = []

        def locked_once(temporary):
            attempts.append(temporary.name)
            if len(attempts) == 1:
                raise PermissionError('synthetic sharing violation')
            cleanup(temporary)

        with patch.object(ci.platform, 'system', return_value='Windows'), \
                patch.object(ci.time, 'sleep') as sleep, \
                patch.object(ci.tempfile.TemporaryDirectory, 'cleanup', locked_once):
            with ci.smoke_workspace() as workspace:
                path = Path(workspace)
                (path / 'synthetic.txt').write_text('test', encoding='utf-8')
            self.assertFalse(path.exists())
        self.assertEqual(len(attempts), 2)
        sleep.assert_called_once_with(0.5)

    def test_workspace_cleanup_errors_are_not_suppressed(self):
        for system, error, count in (
                ('Windows', PermissionError, 4),
                ('Linux', PermissionError, 1),
                ('Windows', OSError, 1)):
            with self.subTest(system=system, error=error):
                temporary = tempfile.TemporaryDirectory()
                self.addCleanup(temporary.cleanup)
                with patch.object(ci.tempfile, 'TemporaryDirectory', return_value=temporary), \
                        patch.object(temporary, 'cleanup', side_effect=error('synthetic failure')) as cleanup, \
                        patch.object(ci.platform, 'system', return_value=system), \
                        patch.object(ci.time, 'sleep') as sleep:
                    with self.assertRaises(error):
                        with ci.smoke_workspace():
                            pass
                self.assertEqual(cleanup.call_count, count)
                self.assertEqual(sleep.call_count, count - 1)

    def test_workspace_cleans_up_after_smoke_failure(self):
        with patch.object(ci.time, 'sleep') as sleep:
            with self.assertRaisesRegex(AssertionError, 'synthetic smoke failure'):
                with ci.smoke_workspace() as workspace:
                    path = Path(workspace)
                    raise AssertionError('synthetic smoke failure')
        self.assertFalse(path.exists())
        sleep.assert_not_called()

    def test_installed_cli_smoke_is_isolated_and_cleans_up(self):
        from gamestack import __version__

        parent_env = dict(os.environ)
        workspaces = set()
        run = subprocess.run
        results = []

        def invoke(args, **kwargs):
            workspace = Path(kwargs['cwd'])
            workspaces.add(workspace)
            search_path = Path(kwargs['env']['PATH'])
            self.assertEqual(search_path.parent, workspace)
            self.assertTrue(search_path.is_dir())
            self.assertEqual(list(search_path.iterdir()), [])
            expected_env = dict(parent_env)
            expected_env.pop('PYTHONPATH', None)
            expected_env['PATH'] = str(search_path)
            self.assertEqual(kwargs['env'], expected_env)
            self.assertTrue(Path(args[0]).is_absolute())
            result = run(args, **kwargs)
            results.append((args, result))
            return result

        with patch.object(ci.subprocess, 'run', side_effect=invoke):
            ci.smoke([sys.executable, '-m', 'gamestack'], __version__)

        self.assertEqual(dict(os.environ), parent_env)
        self.assertEqual(len(workspaces), 1)
        self.assertTrue(all(not path.exists() for path in workspaces))
        listing = next(result for args, result in results if args[-1] == 'list')
        self.assertIn('smoke: unknown (status unavailable)', listing.stdout)
        removal = next(result for args, result in results if args[-2:] == ['rm', 'smoke'])
        self.assertNotEqual(removal.returncode, 0)
        self.assertIn('Removal needs confirmation', removal.stderr)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.version = '0.1.0.dev1'
        self.sha = 'a' * 40
        for suffix in ('-py3-none-any.whl', '.tar.gz', '-linux-x86_64.tar.gz', '-windows-x86_64.zip', '-macos-arm64.tar.gz'):
            (self.directory / ('gamestack-' + self.version + suffix)).write_bytes(b'synthetic artifact')
        ci.checksums(self.directory)
        self.calls = []

    def api(self, method, path, payload=None, binary=None):
        self.calls.append((method, path, payload))
        if path.startswith('releases?'):
            return []
        if method == 'GET':
            return None
        if path == 'git/tags':
            return {'sha': 'b' * 40}
        if path == 'releases/generate-notes':
            return {'body': 'Generated notes'}
        if path == 'releases':
            return {'id': 1, 'upload_url': 'https://uploads.github.com/test{?name}'}
        if binary is not None:
            return {'state': 'uploaded', 'size': len(binary)}
        return {}

    def publish(self, api=None):
        with patch.dict(PUBLISHER, {'api': api or self.api}):
            PUBLISHER['publish'](self.directory, self.version, self.sha, True)

    def test_checksums_and_draft_promotion(self):
        self.publish()
        self.assertEqual(self.calls[-1], ('PATCH', 'releases/1', {'draft': False, 'make_latest': 'false'}))
        create = next(payload for method, path, payload in self.calls if path == 'releases')
        self.assertTrue(create['draft'])
        self.assertTrue(create['prerelease'])
        self.assertEqual(create['target_commitish'], self.sha)
        self.assertEqual(sum(path.startswith('https://uploads') for _, path, _ in self.calls), 6)

    def test_checksum_mismatch_prevents_any_api_write(self):
        next(self.directory.glob('*.whl')).write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.calls, [])

    def test_unexpected_asset_or_missing_checksum_is_rejected(self):
        (self.directory / 'extra').write_text('unexpected')
        with self.assertRaises(ValueError):
            self.publish()
        (self.directory / 'extra').unlink()
        (self.directory / 'SHA256SUMS').write_text('')
        with self.assertRaises(ValueError):
            self.publish()

    def test_duplicate_release_stops_before_tagging(self):
        def api(method, path, payload=None, binary=None):
            self.calls.append((method, path, payload))
            return {'draft': True}
        with self.assertRaisesRegex(RuntimeError, 'already exists'):
            self.publish(api)
        self.assertEqual(len(self.calls), 1)

    def test_draft_in_paginated_listing_blocks_release(self):
        def api(method, path, payload=None, binary=None):
            if path == 'releases?per_page=100&page=1':
                return [{'tag_name': 'v0.0.1'}] * 100
            if path == 'releases?per_page=100&page=2':
                return [{'tag_name': 'v' + self.version, 'draft': True}]
            return self.api(method, path, payload, binary)
        with self.assertRaisesRegex(RuntimeError, 'already exists'):
            self.publish(api)
        self.assertFalse(any(method != 'GET' for method, _, _ in self.calls))

    def test_conflicting_tag_is_never_moved(self):
        def api(method, path, payload=None, binary=None):
            if path.startswith('git/ref/'):
                return {'object': {'type': 'tag', 'sha': 'b' * 40}}
            if path.startswith('git/tags/'):
                return {'object': {'type': 'commit', 'sha': 'c' * 40}}
            return self.api(method, path, payload, binary)
        with self.assertRaisesRegex(RuntimeError, 'another commit'):
            self.publish(api)
        self.assertTrue(all(method == 'GET' for method, _, _ in self.calls))

    def test_same_commit_tag_can_resume(self):
        def api(method, path, payload=None, binary=None):
            if path.startswith('git/ref/'):
                return {'object': {'type': 'tag', 'sha': 'b' * 40}}
            if path.startswith('git/tags/'):
                return {'object': {'type': 'commit', 'sha': self.sha}}
            return self.api(method, path, payload, binary)
        self.publish(api)
        self.assertFalse(any(path in ('git/tags', 'git/refs') for _, path, _ in self.calls))
        self.assertEqual(self.calls[-1][0], 'PATCH')

    def test_interrupted_upload_leaves_draft_unpublished(self):
        def api(method, path, payload=None, binary=None):
            if binary is not None:
                raise RuntimeError('upload interrupted')
            return self.api(method, path, payload, binary)
        with self.assertRaisesRegex(RuntimeError, 'interrupted'):
            self.publish(api)
        self.assertFalse(any(method == 'PATCH' for method, _, _ in self.calls))

    def test_incomplete_upload_leaves_draft_unpublished(self):
        def api(method, path, payload=None, binary=None):
            if binary is not None:
                return {'state': 'starter', 'size': 0}
            return self.api(method, path, payload, binary)
        with self.assertRaisesRegex(RuntimeError, 'incomplete'):
            self.publish(api)
        self.assertFalse(any(method == 'PATCH' for method, _, _ in self.calls))

    def test_version_mismatch_is_rejected(self):
        with patch.object(ci, 'run', return_value='9.9.9'):
            with self.assertRaisesRegex(ValueError, 'disagree'):
                ci.version()

    def test_failed_or_skipped_matrix_blocks_release_gate(self):
        step = WORKFLOW['jobs']['ready']['steps'][0]
        for result in ('failure', 'cancelled', 'skipped'):
            with patch.dict('os.environ', {'RESULTS': '{"test":{"result":"' + result + '"}}'}):
                with self.assertRaises(AssertionError):
                    exec(step['run'], {})

    def test_publication_has_no_checkout_or_project_execution(self):
        job = WORKFLOW['jobs']['publish']
        self.assertEqual(job['permissions'], {'contents': 'write'})
        self.assertEqual(job['needs'], ['metadata', 'ready'])
        self.assertIn("workflow_dispatch", job['if'])
        self.assertEqual(len(job['steps']), 2)
        self.assertNotIn('checkout', job['steps'][0]['uses'])
        for name, job in WORKFLOW['jobs'].items():
            if name != 'publish':
                self.assertNotIn('write', job.get('permissions', {}).values())
            for step in job['steps']:
                if 'uses' in step:
                    self.assertRegex(step['uses'], r'@[a-f0-9]{40}$')

"""Test the exact publishing program embedded in the privileged workflow."""
import importlib.util
from pathlib import Path
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

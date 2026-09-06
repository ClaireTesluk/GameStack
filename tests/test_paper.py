"""Schema 2 contracts, without Docker, game downloads, or EULA acceptance."""
import copy
import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gamestack.cli import configure, main
from gamestack.pack import GameStackError, bind_address, load_pack, validate
from gamestack.runtime import Runtime
import yaml

PACK = Path(__file__).resolve().parents[1] / 'packs/minecraft-paper/pack.yaml'


class PaperTests(unittest.TestCase):
    def setUp(self):
        self.pack = load_pack(PACK)
        self.supplied = {'EULA': 'TRUE', 'OPS': 'TestOwner', 'WHITELIST': 'TestOwner,TestFriend'}

    def values(self):
        with patch('sys.stdin.isatty', return_value=False):
            return configure(self.pack, self.supplied)

    def test_pins_and_secure_defaults(self):
        values = self.values()
        self.assertEqual(values['VERSION'], '26.2')
        self.assertEqual(values['PAPER_BUILD'], '121')
        self.assertEqual(values['ENABLE_RCON'], 'FALSE')
        self.assertEqual(values['ONLINE_MODE'], 'TRUE')
        self.assertEqual(values['EXISTING_WHITELIST_FILE'], 'SKIP')

    def test_fixed_override_even_same_value_rejected(self):
        self.supplied['TYPE'] = 'PAPER'
        with self.assertRaises(GameStackError):
            self.values()

    def test_missing_declined_agreement_and_bad_names(self):
        for key, value in [('EULA', None), ('EULA', 'FALSE'), ('EULA', True), ('OPS', 'ab'), ('OPS', 'a'*17), ('OPS', '../owner'), ('WHITELIST', 'Owner, Friend'), ('WHITELIST', 'Owner,')]:
            with self.subTest(key=key, value=value):
                old = self.supplied.copy()
                if value is None:
                    self.supplied.pop(key)
                else:
                    self.supplied[key] = value
                with self.assertRaises(GameStackError):
                    self.values()
                self.supplied = old

    def test_agreement_default_no(self):
        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value=''):
            with self.assertRaises(GameStackError):
                configure(self.pack, {})

    def test_schema_rejects_invalid_extensions(self):
        for change in [{'startup_timeout': True}, {'startup_timeout': 0}, {'user': '0:0'}]:
            pack = copy.deepcopy(self.pack)
            pack.update(change)
            with self.assertRaises(GameStackError):
                validate(pack)
        pack = copy.deepcopy(self.pack)
        pack['environment']['EULA']['default'] = 'TRUE'
        with self.assertRaises(GameStackError):
            validate(pack)

    def test_addresses(self):
        for value in ['127.0.0.1', '0.0.0.0', '192.168.1.2', '::1', '::']:
            self.assertEqual(bind_address(value), value)
        for value in ['localhost', '1.2.3.999', '224.0.0.1', 'fe80::1%eth0', '255.255.255.255']:
            with self.assertRaises(GameStackError):
                bind_address(value)

    def test_bad_cli_address_no_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            supplied = Path(tmp) / 'values.yaml'
            supplied.write_text(yaml.safe_dump(self.supplied))
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                self.assertEqual(main(['install', str(PACK), '--values', str(supplied), '--bind-address', 'not-an-ip', '--prepare-only']), 1)
            self.assertNotIn('Traceback', output.getvalue())

    @unittest.skipUnless(hasattr(os, 'getuid') and os.getuid() > 0 and os.getgid() > 0, 'requires non-root POSIX owner')
    def test_prepare_inspect_persistence_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Runtime(Path(tmp) / 'instances')
            directory = runtime.prepare(self.pack, 'friends', self.values(), '0.0.0.0')
            metadata = yaml.safe_load((directory / 'instance.yaml').read_text())
            self.assertEqual(metadata['deployment']['user'], f'{os.getuid()}:{os.getgid()}')
            service = yaml.safe_load((directory / 'compose.yaml').read_text())['services']['server']
            self.assertEqual(service['ports'][0]['host_ip'], '0.0.0.0')
            self.assertEqual(service['healthcheck']['start_period'], '600s')
            self.assertEqual((directory / 'compose.yaml').stat().st_mode & 0o777, 0o600)
            self.assertEqual((directory / 'data').stat().st_mode & 0o777, 0o700)
            runtime.inspect('friends')
            with patch.object(runtime, 'doctor'), patch.object(runtime, 'command', return_value='') as command:
                runtime.lifecycle('start', 'friends')
                self.assertIn('600', command.call_args.args[0])
            document = yaml.safe_load((directory / 'compose.yaml').read_text())
            document['services']['server']['environment']['TYPE'] = 'VANILLA'
            (directory / 'compose.yaml').write_text(yaml.safe_dump(document))
            with self.assertRaises(GameStackError):
                runtime.inspect('friends')

    def test_invalid_values_do_not_create_storage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'instances'
            values = self.values()
            values['EULA'] = 'FALSE'
            with self.assertRaises(GameStackError):
                Runtime(root).prepare(self.pack, 'friends', values)
            self.assertFalse(root.exists())

    def test_schema_one_rejects_network_exposure_before_writes(self):
        pack = load_pack(PACK.parents[1] / 'example/pack.yaml')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'instances'
            with self.assertRaises(GameStackError):
                Runtime(root).prepare(pack, 'friends', {'SERVER_NAME': 'Friends', 'SERVER_PASSWORD': 'synthetic'}, '0.0.0.0')
            self.assertFalse(root.exists())

    @unittest.skipUnless(hasattr(os, 'getuid') and os.getuid() > 0 and os.getgid() > 0, 'requires non-root POSIX owner')
    def test_health_failure_retains_files_and_hides_tool_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Runtime(Path(tmp) / 'instances')
            directory = runtime.prepare(self.pack, 'friends', self.values())
            world = directory / 'data' / 'synthetic-world'
            world.write_text('keep me')
            with patch.object(runtime, 'doctor'), patch.object(runtime, 'command', side_effect=GameStackError('synthetic-private-tool-output')):
                with self.assertRaises(GameStackError) as error:
                    runtime.lifecycle('start', 'friends')
            self.assertNotIn('synthetic-private-tool-output', str(error.exception))
            self.assertIn('gamestack status friends', str(error.exception))
            self.assertEqual(world.read_text(), 'keep me')
            self.assertFalse((directory / '.operation.lock').exists())

    @unittest.skipUnless(hasattr(os, 'getuid') and os.getuid() > 0 and os.getgid() > 0, 'requires non-root POSIX owner')
    def test_saved_identity_and_address_checked_on_inspection(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Runtime(Path(tmp) / 'instances')
            directory = runtime.prepare(self.pack, 'friends', self.values())
            # A caller's identity does not silently rewrite the saved identity.
            with patch('gamestack.runtime.os.getuid', return_value=os.getuid() + 1):
                runtime.inspect('friends')
            path = directory / 'instance.yaml'
            original = yaml.safe_load(path.read_text())
            for key, value in [('user', '0:0'), ('bind_address', 'hostname'), ('bind_address', '0.0.0.0')]:
                with self.subTest(key=key, value=value):
                    changed = copy.deepcopy(original)
                    changed['deployment'][key] = value
                    path.write_text(yaml.safe_dump(changed))
                    with self.assertRaises(GameStackError):
                        runtime.inspect('friends')
            path.write_text(yaml.safe_dump(original))
            (directory / 'data').rmdir()  # Only the empty temporary test folder.
            with self.assertRaisesRegex(GameStackError, 'World folder is missing'):
                runtime.inspect('friends')

    def test_lock_matches_distributed_pack(self):
        import json
        lock = json.loads(PACK.with_name('upstream-lock.json').read_text())
        self.assertEqual(self.pack['image'], lock['image']['reference'])
        values = self.values()
        self.assertEqual(values['VERSION'], lock['paper']['version'])
        self.assertEqual(values['PAPER_BUILD'], str(lock['paper']['build']))
        self.assertEqual(lock['paper']['channel'], 'STABLE')

    def test_root_identity_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp, patch('gamestack.runtime.os.getuid', return_value=0, create=True), patch('gamestack.runtime.os.getgid', return_value=0, create=True):
            root = Path(tmp) / 'instances'
            with self.assertRaises(GameStackError):
                Runtime(root).prepare(self.pack, 'friends', self.values())
            self.assertFalse(root.exists())

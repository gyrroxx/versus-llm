import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import versus


class ConfigEnvTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows-specific config path")
    def test_config_env_path_uses_appdata_on_windows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            appdata = Path(tmp) / "Roaming"

            with patch.dict(os.environ, {"APPDATA": str(appdata)}, clear=True):
                self.assertEqual(
                    versus.get_config_env_path(),
                    appdata / "versus-llm" / ".env",
                )

    def test_existing_environment_value_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "cwd"
            cwd.mkdir()
            config_env = Path(tmp) / "config" / ".env"
            config_env.parent.mkdir()
            (cwd / ".env").write_text("OPENROUTER_API_KEY=from-cwd\n", encoding="utf-8")
            config_env.write_text("OPENROUTER_API_KEY=from-config\n", encoding="utf-8")

            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "from-env"}, clear=True):
                with patch("versus.get_config_env_path", return_value=config_env):
                    with patch("pathlib.Path.cwd", return_value=cwd):
                        versus.load_api_key_env()

                self.assertEqual(os.environ["OPENROUTER_API_KEY"], "from-env")

    def test_current_directory_env_wins_over_saved_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "cwd"
            cwd.mkdir()
            config_env = Path(tmp) / "config" / ".env"
            config_env.parent.mkdir()
            (cwd / ".env").write_text("OPENROUTER_API_KEY=from-cwd\n", encoding="utf-8")
            config_env.write_text("OPENROUTER_API_KEY=from-config\n", encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                with patch("versus.get_config_env_path", return_value=config_env):
                    with patch("pathlib.Path.cwd", return_value=cwd):
                        versus.load_api_key_env()

                self.assertEqual(os.environ["OPENROUTER_API_KEY"], "from-cwd")

    def test_saved_config_env_is_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "cwd"
            cwd.mkdir()
            config_env = Path(tmp) / "config" / ".env"
            config_env.parent.mkdir()
            config_env.write_text("OPENROUTER_API_KEY=from-config\n", encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                with patch("versus.get_config_env_path", return_value=config_env):
                    with patch("pathlib.Path.cwd", return_value=cwd):
                        versus.load_api_key_env()

                self.assertEqual(os.environ["OPENROUTER_API_KEY"], "from-config")

    def test_setup_api_key_writes_saved_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_env = Path(tmp) / "config" / ".env"

            with patch("versus.get_config_env_path", return_value=config_env):
                with patch("versus.getpass", return_value="sk-test-key"):
                    with redirect_stdout(io.StringIO()):
                        versus.setup_api_key()

            self.assertEqual(
                config_env.read_text(encoding="utf-8"),
                "OPENROUTER_API_KEY=sk-test-key\n",
            )

    def test_setup_api_key_rejects_empty_input(self) -> None:
        with patch("versus.getpass", return_value="  "):
            with redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    versus.setup_api_key()

        self.assertEqual(raised.exception.code, 1)

    def test_setup_and_login_are_handled_before_argparse(self) -> None:
        for command in ("setup", "login"):
            with self.subTest(command=command):
                with patch.object(sys, "argv", ["versus", command]):
                    with patch("versus.setup_api_key") as setup:
                        with patch("versus.parse_args") as parse_args:
                            versus.main()

                setup.assert_called_once_with()
                parse_args.assert_not_called()


if __name__ == "__main__":
    unittest.main()

import io
import sys
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from unittest.mock import patch

import versus


class RussianUiTextTests(unittest.TestCase):
    def test_missing_key_message_is_in_russian(self) -> None:
        self.assertIn("API-ключ OpenRouter не настроен.", versus.MISSING_KEY_MSG)
        self.assertIn("versus setup", versus.MISSING_KEY_MSG)
        self.assertNotIn("OPENROUTER_API_KEY is not set", versus.MISSING_KEY_MSG)

    def test_setup_prompt_is_in_russian(self) -> None:
        with patch("versus.get_config_env_path") as config_path:
            config_path.return_value.parent.mkdir.return_value = None
            config_path.return_value.write_text.return_value = None
            with patch("versus.getpass", return_value="sk-test-key") as getpass:
                with redirect_stdout(io.StringIO()):
                    versus.setup_api_key()

        getpass.assert_called_once_with("Вставь API-ключ OpenRouter: ")

    def test_help_text_is_in_russian(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit):
                versus.parse_args(["--help"])

        help_text = output.getvalue()
        self.assertIn("Два LLM спорят по вопросу", help_text)
        self.assertIn("вопрос для спора", help_text)
        self.assertIn("путь к файлу с контекстом", help_text)
        self.assertNotIn("the question to debate", help_text)

    def test_argparse_error_is_in_russian(self) -> None:
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["versus", "--bad"]):
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit):
                    versus.parse_args(["--bad"])

        error_text = stderr.getvalue()
        self.assertIn("ошибка", error_text)
        self.assertIn("неизвестные аргументы", error_text)
        self.assertNotIn("unrecognized arguments", error_text)


if __name__ == "__main__":
    unittest.main()

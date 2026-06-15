import unittest

import versus


class DefaultBehaviorTests(unittest.TestCase):
    def test_default_models_assign_gpt_oss_to_agent_a_and_gemma_to_agent_b(self) -> None:
        self.assertEqual(versus.DEFAULT_MODEL_A, "openai/gpt-oss-120b:free")
        self.assertEqual(versus.DEFAULT_MODEL_B, "google/gemma-4-31b-it:free")

    def test_judge_prompt_requires_original_question_language(self) -> None:
        self.assertIn("original question", versus.SYSTEM_JUDGE)
        self.assertIn("Russian", versus.SYSTEM_JUDGE)


if __name__ == "__main__":
    unittest.main()

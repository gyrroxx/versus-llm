import unittest

import versus


class DefaultBehaviorTests(unittest.TestCase):
    def test_default_models_assign_requested_models_to_agents_and_judge(self) -> None:
        self.assertEqual(versus.DEFAULT_MODEL_A, "nvidia/nemotron-3-super-120b-a12b:free")
        self.assertEqual(versus.DEFAULT_MODEL_B, "openai/gpt-oss-120b:free")
        self.assertEqual(versus.DEFAULT_MODEL_JUDGE, "google/gemma-4-31b-it:free")

    def test_default_version_is_1_3_0(self) -> None:
        self.assertEqual(versus.VERSION, "1.3.0")

    def test_models_arg_accepts_agent_and_judge_models(self) -> None:
        args = versus.parse_args([
            "test question",
            "--models",
            "model-a",
            "model-b",
            "judge-model",
        ])

        self.assertEqual(args.models, ["model-a", "model-b", "judge-model"])

    def test_transcript_accepts_two_models_and_records_default_judge(self) -> None:
        transcript = versus.build_transcript_md(
            "test question",
            ["model-a", "model-b"],
            None,
            1,
            [],
            "verdict",
        )

        self.assertIn("model-a", transcript)
        self.assertIn("model-b", transcript)
        self.assertIn("google/gemma-4-31b-it:free", transcript)

    def test_followup_user_content_includes_debate_verdict_and_question(self) -> None:
        content = versus.followup_user_content(
            "original topic",
            [{"speaker": "Agent A", "round": 1, "text": "agent answer"}],
            "judge verdict",
            [],
            "follow-up question",
        )

        self.assertIn("original topic", content)
        self.assertIn("agent answer", content)
        self.assertIn("judge verdict", content)
        self.assertIn("follow-up question", content)
        self.assertIn("Ответь на уточняющий вопрос", content)

    def test_transcript_records_followups(self) -> None:
        transcript = versus.build_transcript_md(
            "test question",
            ["model-a", "model-b", "judge-model"],
            None,
            1,
            [],
            "verdict",
            [{"question": "А если проект маленький?", "answer": "Тогда проще выбрать A."}],
        )

        self.assertIn("Уточняющие вопросы", transcript)
        self.assertIn("А если проект маленький?", transcript)
        self.assertIn("Тогда проще выбрать A.", transcript)

    def test_followup_limit_allows_ten_questions(self) -> None:
        self.assertEqual(versus.MAX_FOLLOWUPS, 10)
        self.assertFalse(versus.followup_limit_reached([{}] * 9))
        self.assertTrue(versus.followup_limit_reached([{}] * 10))

    def test_thinking_frame_animates_dots(self) -> None:
        self.assertEqual(versus.thinking_frame("Агент B думает", 0), "Агент B думает.")
        self.assertEqual(versus.thinking_frame("Агент B думает", 1), "Агент B думает..")
        self.assertEqual(versus.thinking_frame("Агент B думает", 2), "Агент B думает...")
        self.assertEqual(versus.thinking_frame("Агент B думает", 3), "Агент B думает.")

    def test_judge_prompt_requires_original_question_language(self) -> None:
        self.assertIn("original question", versus.SYSTEM_JUDGE)
        self.assertIn("Russian", versus.SYSTEM_JUDGE)

    def test_agent_prompts_push_direct_argument_attacks(self) -> None:
        for prompt in (versus.SYSTEM_A, versus.SYSTEM_B):
            self.assertIn("attack the opponent's reasoning", prompt)
            self.assertIn("No polite balance", prompt)
            self.assertIn("Do not invent facts", prompt)

    def test_judge_prompt_requires_neutral_evidence_based_verdict(self) -> None:
        self.assertIn("strictly neutral", versus.SYSTEM_JUDGE)
        self.assertIn("Judge only correctness", versus.SYSTEM_JUDGE)
        self.assertIn("Ignore confidence, aggression, style, and rhetoric", versus.SYSTEM_JUDGE)


if __name__ == "__main__":
    unittest.main()

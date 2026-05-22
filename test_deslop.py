"""Tests for deslop. Run: python3 -m unittest -v  (no dependencies)."""
import unittest

import deslop


SLOP = (
    "In today's fast-paced world, this is a pivotal moment. It's not just about "
    "speed — it's about precision. Let's dive in. Experts agree that 90% of teams "
    "delve into this. Furthermore, we must leverage robust, comprehensive systems. "
    "In conclusion, the journey matters."
)

HUMAN = (
    "I missed the train by a minute. The next one came forty minutes later, which "
    "gave me time to notice the woman selling roasted corn on the platform. She'd "
    "been there every morning for years, she said, and nobody ever bought before 8. "
    "I bought two. They were burnt on one side. Best thing I ate that week."
)


class TestSegmentation(unittest.TestCase):
    def test_sentences(self):
        self.assertEqual(len(deslop.split_sentences("One. Two! Three?")), 3)

    def test_abbrev_not_split(self):
        s = deslop.split_sentences("Dr. Smith arrived. He was late.")
        self.assertEqual(len(s), 2)

    def test_syllables(self):
        self.assertEqual(deslop.count_syllables("cat"), 1)
        self.assertEqual(deslop.count_syllables("table"), 2)
        self.assertGreaterEqual(deslop.count_syllables("comprehensive"), 4)

    def test_strip_markdown(self):
        self.assertNotIn("xyz", deslop.strip_markdown("text `xyz` more"))


class TestDetectors(unittest.TestCase):
    def test_antithesis(self):
        f = deslop.detect_antithesis("It's not about money — it's about freedom.")
        self.assertTrue(f)
        self.assertEqual(f[0].category, "antithesis")

    def test_no_antithesis_in_plain(self):
        self.assertEqual(deslop.detect_antithesis("The cat sat on the mat."), [])

    def test_banned_vocab(self):
        f = deslop.detect_vocab("We will delve into this robust tapestry.")
        hit = {x.message for x in f}
        self.assertTrue(any("delve" in m for m in hit))
        self.assertTrue(any("robust" in m for m in hit))
        self.assertTrue(any("tapestry" in m for m in hit))

    def test_manufactured_numbers(self):
        f = deslop.detect_numbers("We hit 10,000 users with 50% retention.")
        self.assertTrue(any("round" in x.message for x in f))
        self.assertTrue(any("percentage" in x.message for x in f))

    def test_messy_numbers_not_flagged_as_pct(self):
        f = deslop.detect_numbers("Retention was 37%.")
        self.assertFalse(any("percentage" in x.message for x in f))

    def test_signposts(self):
        f = deslop.detect_signposts("In conclusion, we won.")
        self.assertTrue(f)


class TestMetrics(unittest.TestCase):
    def test_cv(self):
        self.assertEqual(deslop._cv([5, 5, 5]), 0.0)
        self.assertGreater(deslop._cv([2, 20, 4, 30]), 0.5)

    def test_flesch_range(self):
        fre = deslop.flesch_reading_ease(HUMAN, deslop.split_sentences(HUMAN))
        self.assertGreater(fre, 0)
        self.assertLess(fre, 121)

    def test_hapax_rate(self):
        self.assertEqual(deslop.hapax_rate(["a", "a", "b"]), 0.5)

    def test_mtld_positive(self):
        self.assertGreater(deslop.mtld(deslop.words(HUMAN)), 0)


class TestScoring(unittest.TestCase):
    def test_slop_scores_low(self):
        self.assertLess(deslop.analyze(SLOP).score, 55)

    def test_human_scores_high(self):
        self.assertGreaterEqual(deslop.analyze(HUMAN).score, 80)

    def test_separation(self):
        self.assertGreater(deslop.analyze(HUMAN).score, deslop.analyze(SLOP).score)

    def test_grade_labels(self):
        self.assertEqual(deslop.grade_for(95), "human")
        self.assertEqual(deslop.grade_for(10), "AI slop")

    def test_report_shape(self):
        r = deslop.analyze(HUMAN)
        self.assertIn("words", r.stats)
        self.assertIn("flesch_reading_ease", r.stats)


class TestProfile(unittest.TestCase):
    def test_profile_keys(self):
        p = deslop.profile(HUMAN)
        for k in ("mean_sentence_len", "burstiness_cv", "mtld", "hapax_rate",
                  "flesch_reading_ease", "top_content_words"):
            self.assertIn(k, p)

    def test_target_line(self):
        line = deslop.profile_target_line(deslop.profile(HUMAN))
        self.assertIn("Target voice", line)


class TestCLI(unittest.TestCase):
    def test_min_score_gate_fails_on_slop(self):
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            rc = deslop.main(["--quiet", "--min-score", "80", "examples/slop.md"])
        self.assertEqual(rc, 1)

    def test_min_score_gate_passes_on_voiced(self):
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            rc = deslop.main(["--quiet", "--min-score", "80", "examples/voiced.md"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()

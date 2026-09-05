import unittest

from app.services.vision import (
    ImageMetadata,
    ImageQuality,
    ShotSignals,
    assess_photo_set,
    classify_shot,
)


def metadata(image_id: str) -> ImageMetadata:
    return ImageMetadata(image_id, f"{image_id}.png", "png", 1000, 1000, 100)


def quality(score: float) -> ImageQuality:
    return ImageQuality(score, score, score, score, score)


class TestShotClassifier(unittest.TestCase):
    def test_explicit_context_signal_is_lifestyle(self):
        result = classify_shot(metadata("life"), quality(80), ShotSignals(has_person_or_context=True))
        self.assertEqual(result.photo_type, "lifestyle")

    def test_explicit_detail_signal_is_detail(self):
        result = classify_shot(metadata("detail"), quality(80), ShotSignals(close_crop=True))
        self.assertEqual(result.photo_type, "detail")

    def test_weak_default_is_conservative_primary_candidate(self):
        result = classify_shot(metadata("primary"), quality(80))
        self.assertEqual(result.photo_type, "primary")
        self.assertLess(result.confidence, 0.6)


class TestPhotoSetAssessment(unittest.TestCase):
    def test_assessment_reports_missing_types_and_best_primary(self):
        classifications = [
            classify_shot(metadata("one"), quality(90)),
            classify_shot(metadata("two"), quality(70), ShotSignals(close_crop=True)),
        ]
        result = assess_photo_set(
            classifications,
            {"one.png": quality(90), "two.png": quality(70)},
        )

        self.assertEqual(result.recommended_primary, "one.png")
        self.assertIn("lifestyle", result.missing_types)
        self.assertIn("side_back", result.missing_types)
        self.assertGreaterEqual(result.media_readiness_score, 0)
        self.assertLessEqual(result.media_readiness_score, 100)

    def test_duplicate_images_are_excluded_from_primary_recommendation(self):
        classification = classify_shot(metadata("one"), quality(90))
        result = assess_photo_set([classification], {"one.png": quality(90)}, {"one.png"})

        self.assertIsNone(result.recommended_primary)
        self.assertIn("duplicate_images_present", result.issues)


if __name__ == "__main__":
    unittest.main()

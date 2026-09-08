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
        result = classify_shot(metadata("life"), quality(80), ShotSignals(has_lifestyle_context=True))
        self.assertEqual(result.photo_type, "lifestyle")

    def test_person_alone_is_not_lifestyle(self):
        result = classify_shot(metadata("person"), quality(80), ShotSignals(has_person=True))
        self.assertNotEqual(result.photo_type, "lifestyle")

    def test_worn_or_used_product_is_lifestyle(self):
        result = classify_shot(metadata("used"), quality(80), ShotSignals(is_being_worn_or_used=True))
        self.assertEqual(result.photo_type, "lifestyle")

    def test_explicit_detail_signal_is_detail(self):
        result = classify_shot(metadata("detail"), quality(80), ShotSignals(close_crop=True))
        self.assertEqual(result.photo_type, "detail")

    def test_missing_semantic_signal_is_not_called_primary(self):
        result = classify_shot(metadata("primary"), quality(80))
        self.assertEqual(result.photo_type, "other")
        self.assertEqual(result.confidence, 0.0)

    def test_complete_product_without_lifestyle_context_is_primary(self):
        result = classify_shot(
            metadata("complete"),
            quality(80),
            ShotSignals(shows_complete_product=True),
        )
        self.assertEqual(result.photo_type, "primary")

    def test_close_crop_incomplete_product_is_detail(self):
        result = classify_shot(
            metadata("detail"),
            quality(80),
            ShotSignals(close_crop=True, shows_complete_product=False),
        )
        self.assertEqual(result.photo_type, "detail")

    def test_close_crop_complete_product_is_still_detail(self):
        result = classify_shot(
            metadata("craftsmanship"),
            quality(80),
            ShotSignals(close_crop=True, shows_complete_product=True),
        )
        self.assertEqual(result.photo_type, "detail")

    def test_side_or_back_is_side_back(self):
        result = classify_shot(
            metadata("side"),
            quality(80),
            ShotSignals(shows_side_or_back=True),
        )
        self.assertEqual(result.photo_type, "side_back")

    def test_outdoor_table_complete_product_is_primary(self):
        result = classify_shot(
            metadata("table"),
            quality(80),
            ShotSignals(
                has_person=False,
                is_being_worn_or_used=False,
                has_lifestyle_context=False,
                shows_complete_product=True,
            ),
        )
        self.assertEqual(result.photo_type, "primary")


class TestPhotoSetAssessment(unittest.TestCase):
    def test_assessment_reports_missing_types_and_best_primary(self):
        classifications = [
            classify_shot(metadata("one"), quality(90), ShotSignals(shows_complete_product=True)),
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
        classification = classify_shot(metadata("one"), quality(90), ShotSignals(shows_complete_product=True))
        result = assess_photo_set([classification], {"one.png": quality(90)}, {"one.png"})

        self.assertIsNone(result.recommended_primary)
        self.assertIn("duplicate_images_present", result.issues)


if __name__ == "__main__":
    unittest.main()

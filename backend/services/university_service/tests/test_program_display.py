from django.test import SimpleTestCase

from services.university_service.program_display import format_program_display_names


class ProgramDisplayHelperTests(SimpleTestCase):
    def test_engineering_ee_expansion_is_contextual(self):
        self.assertEqual(
            format_program_display_names(["Engineering (EE)"]),
            ["Engineering — Electrical Engineering"],
        )
        self.assertEqual(
            format_program_display_names(["Business (EE)"]),
            ["Business — EE"],
        )

    def test_stray_parentheses_are_removed_without_inventing_parent(self):
        self.assertEqual(format_program_display_names(["Mechanical)"]), ["Mechanical"])


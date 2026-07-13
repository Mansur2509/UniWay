import re
from pathlib import Path

from django.test import SimpleTestCase


class UniversityImportWorkflowSecurityTests(SimpleTestCase):
    def test_dispatch_inputs_are_not_interpolated_inside_shell_blocks(self):
        repository_root = Path(__file__).resolve().parents[3]
        workflow = (
            repository_root / ".github" / "workflows" / "university-import.yml"
        ).read_text(encoding="utf-8")
        run_blocks = re.findall(
            r"(?ms)^\s+run: \|\n((?:\s{10,}.*(?:\n|$))*)",
            workflow,
        )

        self.assertTrue(run_blocks)
        self.assertNotIn("${{ inputs.", "\n".join(run_blocks))
        self.assertIn('dataset_path="$(realpath -m', workflow)
        self.assertIn('! "$INPUT_LIMIT" =~ ^[1-9][0-9]{0,5}$', workflow)
        self.assertIn("Dataset path escaped the repository", workflow)

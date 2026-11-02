import importlib.util
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest

spec = importlib.util.spec_from_file_location('attribution', Path(__file__).with_name('reviewer_attribution.py'))
attribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attribution)


class AttributionTests(unittest.TestCase):
    def test_signoff_changes_with_execution_fields(self):
        settings = {'model': 'gpt-1.2-example', 'model_reasoning_effort': 'low'}
        self.assertEqual(attribution.native_attribution(settings), 'Reviewed by GPT-1.2 Example low.')
        settings.update(model='gpt-2.3-other', model_reasoning_effort='high')
        self.assertEqual(attribution.native_attribution(settings), 'Reviewed by GPT-2.3 Other high.')

    def test_unknown_identifier_is_preserved(self):
        settings = {'model': 'example-model', 'model_reasoning_effort': 'medium'}
        self.assertEqual(attribution.native_attribution(settings), 'Reviewed by example-model medium.')

    def test_native_reviewer_entrypoints_derive_their_own_settings(self):
        for role in ('pr-review', 'pr-review-high', 'pr-risk', 'pr-review-approach', 'pr-review-approach-high'):
            with self.subTest(role=role):
                settings = tomllib.loads((attribution.AGENTS / (role + '.toml')).read_text())
                result = subprocess.run([sys.executable, str(Path(attribution.__file__)), role],
                                        capture_output=True, text=True, check=True)
                contribution = 'Approach analysis by' if role.startswith('pr-review-approach') else 'Reviewed by'
                self.assertEqual(result.stdout.strip(), attribution.native_attribution(settings, contribution))


if __name__ == '__main__':
    unittest.main()

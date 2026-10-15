import importlib.util
from pathlib import Path
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


if __name__ == '__main__':
    unittest.main()

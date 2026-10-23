from django.test import TestCase

from problembank.models import Problems


class QuestionDescriptionTests(TestCase):
    def test_non_numeric_id_is_404(self):
        self.assertEqual(self.client.get("/questions/abc/").status_code, 404)

    def test_unknown_id_is_404(self):
        self.assertEqual(self.client.get("/questions/999/").status_code, 404)

    def test_known_id_renders(self):
        Problems.objects.create(
            q_no=1, q_title="Two Sum", q_description="d", q_input_format="i",
            q_output_format="o", q_sample_io="s", q_tag="t",
        )
        self.assertEqual(self.client.get("/questions/1/").status_code, 200)

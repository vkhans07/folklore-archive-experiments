import unittest

from folklore_eval.evaluate import score_document
from folklore_eval.matching import region_pairs
from folklore_eval.validation import parse_response


def row(label="folklore_item", page=0, text="Café tale.", box=None):
    return {"page_num": page, "label": label, "text": text, "bbox": box or [0.1, 0.1, 0.4, 0.4]}


class EvaluationTests(unittest.TestCase):
    def test_perfect_with_nfc_and_whitespace(self):
        refs = [row(text="Café  tale.")]
        preds = [row(text="Cafe\u0301 tale.")]
        result = score_document(refs, preds)
        self.assertEqual(result["text_f1"], 1)
        self.assertEqual(result["box_f1"], 1)
        self.assertEqual(result["box_matched_char_edit_total"], 0)

    def test_duplicate_prediction_is_false_positive(self):
        result = score_document([row()], [row(), row()])
        self.assertEqual((result["text_tp"], result["text_fp"], result["text_fn"]), (1, 1, 0))
        self.assertEqual((result["box_tp"], result["box_fp"], result["box_fn"]), (1, 1, 0))

    def test_missing_extra_and_wrong_text(self):
        refs = [row(), row(text="Second", box=[0.5, 0.5, 0.8, 0.8])]
        preds = [row(text="Cafe tale."), row(text="Extra", box=[0.01, 0.7, 0.09, 0.9])]
        result = score_document(refs, preds)
        self.assertEqual((result["text_tp"], result["text_fp"], result["text_fn"]), (0, 2, 2))
        self.assertEqual((result["box_tp"], result["box_fp"], result["box_fn"]), (1, 1, 1))
        self.assertGreater(result["box_matched_char_edit_total"], 0)

    def test_wrong_label_and_page_cannot_match(self):
        result = score_document([row()], [row(label="collector_name"), row(page=1)])
        self.assertEqual(result["text_tp"], 0)
        self.assertEqual(result["box_tp"], 0)

    def test_cardinality_precedes_iou(self):
        refs = [row(box=[0, 0, .6, .5]), row(box=[.4, 0, 1, .5])]
        preds = [row(box=[0, 0, 1, .5]), row(box=[0, 0, .6, .5])]
        self.assertEqual(len(region_pairs(refs, preds, .5)), 2)

    def test_invalid_boxes_and_types(self):
        labels = {"folklore_item"}
        for bad in ([.5, .1, .5, .4], [-.1, 0, .4, .4], [0, 0, 2, 1], [0, 0, 1]):
            value, errors, parsed = parse_response('{"annotations": [{"page_num": 0, "label": "folklore_item", "text": "x", "bbox": %s}]}' % str(bad), labels, 1)
            self.assertTrue(parsed)
            self.assertIsNone(value)
            self.assertTrue(errors)
        value, errors, parsed = parse_response('{"annotations": [{"page_num": true, "label": "folklore_item", "text": "x", "bbox": [0,0,1,1]}]}', labels, 1)
        self.assertTrue(parsed)
        self.assertIsNone(value)

    def test_malformed_json_and_wrong_vocabulary(self):
        self.assertFalse(parse_response('{"annotations": [', {"folklore_item"}, 1)[2])
        value, errors, parsed = parse_response('{"annotations": [{"page_num": 0, "label": "unknown", "text": "x", "bbox": [0,0,1,1]}]}', {"folklore_item"}, 1)
        self.assertTrue(parsed)
        self.assertIsNone(value)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()

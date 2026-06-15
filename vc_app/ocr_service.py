import numpy as np
from PIL import Image
from .utils.extractor import EntityExtractor

_reader = None


def get_reader():
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        except Exception as e:
            raise RuntimeError(f"EasyOCR failed to load: {str(e)}")
    return _reader


def process_visiting_card(image_path: str) -> dict:
    reader = get_reader()

    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img, dtype=np.uint8)

    results = reader.readtext(img_array, detail=1)

    if not results:
        return {
            'name': 'Unknown', 'email': None, 'mobile': None,
            'website': None, 'designation': None, 'company': None,
            'address': None, 'raw_text': '', 'ocr_confidence': 0,
        }

    lines = [text for (_, text, _) in results]
    confidences = [conf for (_, _, conf) in results]
    raw_text = '\n'.join(lines)
    avg_conf = round(sum(confidences) / len(confidences) * 100, 2)

    fields = EntityExtractor(raw_text).extract()
    fields['raw_text'] = raw_text
    fields['ocr_confidence'] = avg_conf
    return fields

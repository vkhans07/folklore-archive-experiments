# Reference data corrections

## Taiwan Holiday Lore

The active sample export in `JSONs/Taiwan Holiday Lore.json` now includes two previously omitted page 2 regions (zero-based `page_num: 1`):

- `informant_name`: “Linda Wei Chen,” repeated in the page header. Its box is the union of the supplied OCR word boxes.
- `collector_annotation`: the final paragraph, beginning “Every year around this date…” and ending “…we have Chi Shi.” Its box is the union of the supplied OCR word boxes.

The text and normalized boxes were copied from `outputs/inputs/00001_09_Taiwan_holiday_lore__93.json`. The Taiwan active-reference count in `config/integrity.json` was updated from 17 to 19. Other source annotations were left unchanged.

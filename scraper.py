import csv
import json
import os
import re
from datetime import datetime, date
from urllib.request import Request, urlopen

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1AOD6mSBcrS63NnWctlQhvtAAgqQ23sYjSYkNVKOBlrs/export?format=csv&gid=0'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'latest.json')


def normalize_header(value):
    text = (value or '').strip().lower()
    text = text.replace('(', ' ').replace(')', ' ')
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')


def clean_text(value):
    if value is None:
        return ''
    return str(value).strip().replace('\u00a0', ' ')


def parse_date(value):
    text = clean_text(value)
    if not text:
        return None
    text = text.replace('  ', ' ')
    text = text.replace('/', '.')
    text = text.replace('-', '.')
    text = text.replace('..', '.')

    patterns = [
        '%d.%m.%Y',
        '%d.%m.%y',
        '%d.%m.%Y %H:%M:%S',
        '%d.%m.%y %H:%M:%S',
        '%d/%m/%Y',
        '%d/%m/%y',
        '%Y-%m-%d',
        '%Y/%m/%d',
    ]

    for fmt in patterns:
        try:
            parsed = datetime.strptime(text, fmt).date()
            return parsed.replace(year=2026)
        except ValueError:
            pass

    digits = re.findall(r'\d+', text)
    if len(digits) >= 2:
        try:
            if len(digits[0]) == 4:
                parsed = datetime.strptime(f"{digits[0]}-{digits[1]}-{digits[2]}", '%Y-%m-%d').date()
                return parsed.replace(year=2026)
            if len(digits[1]) == 4:
                parsed = datetime.strptime(f"{digits[0]}-{digits[1]}-{digits[2]}", '%d-%m-%Y').date()
                return parsed.replace(year=2026)
        except Exception:
            pass

    return None


def safe_days_since(value):
    d = parse_date(value)
    if not d:
        return None
    age = (date.today() - d).days
    return max(0, age)


OFFICIAL_ALIASES = {
    'sunil': 'Sunil',
    'sunil sharma': 'Sunil',
    'sh sunil sharma': 'Sunil',
    'sunil sharma ': 'Sunil',
    'vipin': 'Vipin',
    'vipin udaiwal': 'Vipin',
    'vipi n udaiwal': 'Vipin',
    'hemraj': 'Hemraj',
    'hemraj choudhary': 'Hemraj',
    'sh hemraj choudhary': 'Hemraj',
    'anil': 'Anil',
    'anil kumar': 'Anil',
    'rajeev': 'Rajeev',
    'rajeev udaiwal': 'Rajeev',
    'on file': 'On file',
    'onfile': 'On file',
    'on file ': 'On file',
    'misc': 'Miscellaneous',
    'miscellaneous': 'Miscellaneous',
    'others': 'Miscellaneous',
    'other': 'Miscellaneous',
}


def normalize_official_name(raw_name):
    text = clean_text(raw_name).lower().strip()
    if not text:
        return 'Miscellaneous'

    for key, mapped in OFFICIAL_ALIASES.items():
        if text == key or key in text:
            return mapped

    if any(token in text for token in ['sunil']):
        return 'Sunil'
    if any(token in text for token in ['vipin']):
        return 'Vipin'
    if any(token in text for token in ['hemraj']):
        return 'Hemraj'
    if any(token in text for token in ['anil']):
        return 'Anil'
    if any(token in text for token in ['rajeev']):
        return 'Rajeev'
    if any(token in text for token in ['file', 'on file']):
        return 'On file'
    return 'Miscellaneous'


def is_pending_row(row):
    if not row.get('Date of Reciept') and not row.get('date_of_reciept'):
        return False
    status = clean_text(row.get('Remarks/Status') or row.get('remarks_status') or '').lower()
    if not status:
        return True
    blocked = ['closed', 'completed', 'disposed', 'processed', 'filed', 'settled', 'not pertained', 'not required']
    if any(word in status for word in blocked):
        return False
    return True


def fetch_csv_text(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, timeout=30) as response:
        raw = response.read()
    return raw.decode('utf-8-sig', 'replace')


def build_rows():
    csv_text = fetch_csv_text(SHEET_URL)
    lines = csv_text.splitlines()
    header_index = None

    for i, line in enumerate(lines):
        lower = line.lower()
        if 'date of reciept' in lower or 'date of receipt' in lower:
            header_index = i
            break

    if header_index is None:
        raise ValueError('Could not find the header row in the Google Sheet export.')

    header_line = lines[header_index]
    data_lines = lines[header_index + 1:]
    reader = csv.DictReader(data_lines, fieldnames=header_line.split(','))
    processed = []

    for row in reader:
        normalized = {}
        for key, value in row.items():
            normalized[normalize_header(key)] = value

        if not normalized:
            continue

        receipt = clean_text(normalized.get('date_of_reciept', '') or normalized.get('date_of_reciept_') or '')
        if not receipt:
            continue

        official_raw = clean_text(
            normalized.get('remark_of_dak_officials_svs')
            or normalized.get('remark_of_dak_officials_svs_')
            or normalized.get('remark_of_dak_officials_svs__')
            or normalized.get('remark_of_dak_officials_svs___')
            or normalized.get('remark_of_dak_officials_svs____')
            or '')
        official = normalize_official_name(official_raw)

        parsed_receipt = parse_date(receipt)
        date_value = parsed_receipt.strftime('%d.%m.%Y') if parsed_receipt else receipt
        age_days = safe_days_since(date_value)
        if age_days is None:
            continue

        from_whom = clean_text(normalized.get('from_whom_received') or normalized.get('from_whom_received_') or '')
        subject = clean_text(normalized.get('subject') or normalized.get('subject_') or '')
        remarks = clean_text(normalized.get('remarks_status') or normalized.get('remarks_status_') or '')
        serial_no = clean_text(normalized.get('serial_no') or normalized.get('serial_no_') or '')

        if not is_pending_row(normalized):
            continue

        processed.append({
            'serial_no': serial_no,
            'date_of_receipt': date_value,
            'date_of_receipt_iso': parse_date(date_value).isoformat() if parse_date(date_value) else '',
            'from_whom_received': from_whom,
            'subject': subject,
            'official': official,
            'remarks_status': remarks,
            'age_days': age_days,
            'red_flag': age_days > 7,
            'pending': True,
        })

    return processed


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    rows = build_rows()

    official_counts = {}
    for item in rows:
        official = item['official'] or 'Unassigned'
        official_counts[official] = official_counts.get(official, 0) + 1

    summary = {
        'total_pending': len(rows),
        'red_flag_count': sum(1 for row in rows if row['red_flag']),
        'official_count': len(official_counts),
        'max_age_days': max((row['age_days'] for row in rows), default=0),
        'avg_age_days': round(sum(row['age_days'] for row in rows) / len(rows), 1) if rows else 0,
    }

    payload = {
        'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source_url': SHEET_URL,
        'summary': summary,
        'officials': [{'name': name, 'count': count} for name, count in sorted(official_counts.items(), key=lambda x: (-x[1], x[0]))],
        'rows': sorted(rows, key=lambda x: (parse_date(x['date_of_receipt']) or date.min, x['age_days']), reverse=True),
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f'Fetched {len(rows)} pending rows and saved to {OUTPUT_FILE}')


if __name__ == '__main__':
    main()

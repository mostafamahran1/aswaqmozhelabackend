import re
import unicodedata

_DIACRITICS = re.compile(r'[\u064B-\u0652\u0670\u0640]')
_NON_WORD = re.compile(r'[^\w\s]+', re.UNICODE)
_ALEF = str.maketrans({
    'أ': 'ا',
    'إ': 'ا',
    'آ': 'ا',
    'ٱ': 'ا',
    'ى': 'ي',
    'ة': 'ه',
    'ؤ': 'و',
    'ئ': 'ي',
})

# Each group is the same thing said in another spelling or language.
_GROUPS = (
    ('nike', 'نايك'),
    ('dior', 'ديور'),
    ('burberry', 'بربري'),
    ('lacoste', 'لاكوست'),
    ('sauvage', 'سوفاج'),
    ('azzaro', 'ازارو'),
    ('armani', 'ارماني'),
    ('invictus', 'انفكتوس'),
    ('caterpillar', 'كاتربيلر'),
    ('tetris', 'تتريس'),
    ('squishy', 'سكويشي'),
    ('shark', 'قرش'),
    ('perfume', 'fragrance', 'oud', 'عطر', 'عطور', 'عود', 'بارفان', 'برفان'),
    ('coffee', 'قهوه'),
    ('phone', 'mobile', 'موبايل', 'تليفون', 'هاتف'),
    ('kitchen', 'مطبخ'),
    ('helicopter', 'طياره', 'هليكوبتر'),
    ('piano', 'بيانو'),
    ('car', 'cars', 'عربية', 'عربيه', 'سياره'),
    ('toy', 'toys', 'لعبه', 'لعب', 'العاب'),
    ('game', 'لعبه'),
    ('gift', 'gifts', 'هدايا', 'هديه'),
    ('ice', 'ايس'),
    ('cream', 'كريم'),
    ('white', 'ابيض'),
    ('black', 'اسود'),
    ('gold', 'ذهبي', 'دهب'),
    ('silver', 'فضي'),
    ('bubble', 'فقاعات', 'فقاعه'),
    ('educational', 'تعليمي'),
    ('remote', 'ريموت'),
    ('puzzle', 'بازل'),
    ('socks', 'شراب', 'شرابات'),
    ('veil', 'طرحة', 'طرحه'),
    ('book', 'كتاب', 'كتب'),
    ('food', 'اكل', 'طعام'),
    ('fruit', 'فاكهة', 'فاكهه'),
    ('spice', 'توابل', 'بهارات'),
)


def normalize(text):
    text = unicodedata.normalize('NFKC', text or '')
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Cf')
    text = text.translate(_ALEF)
    text = _DIACRITICS.sub('', text).lower()
    text = _NON_WORD.sub(' ', text)
    return ' '.join(text.split())


def _bare(token):
    if token.startswith('ال') and len(token) > 3:
        return token[2:]
    return token


def _tokens(text):
    words = []
    for raw in normalize(text).split():
        word = _bare(raw)
        if len(word) >= 2:
            words.append(word)
    return words


def _build_synonyms():
    groups = []
    for group in _GROUPS:
        folded = {_bare(normalize(word)) for word in group}
        folded.discard('')
        merged = False
        for existing in groups:
            if existing & folded:
                existing.update(folded)
                merged = True
                break
        if not merged:
            groups.append(set(folded))
    synonyms = {}
    for group in groups:
        for word in group:
            synonyms[word] = group
    return synonyms


_SYNONYMS = _build_synonyms()


def _expand(token):
    return _SYNONYMS.get(token, {token})


def _allowance(left, right):
    shorter = min(len(left), len(right))
    longer = max(len(left), len(right))
    if shorter < 3 or longer - shorter > 2:
        return 0
    if longer >= 7:
        return 2
    if longer >= 4:
        return 1
    return 0


def _distance(left, right, limit):
    if abs(len(left) - len(right)) > limit:
        return limit + 1
    before = None
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        row_best = current[0]
        for j, right_char in enumerate(right, start=1):
            cost = 0 if left_char == right_char else 1
            value = min(current[j - 1] + 1, previous[j] + 1, previous[j - 1] + cost)
            if (
                before is not None
                and j > 1
                and left_char == right[j - 2]
                and left[i - 2] == right_char
            ):
                value = min(value, before[j - 2] + 1)
            current.append(value)
            if value < row_best:
                row_best = value
        if row_best > limit:
            return limit + 1
        before = previous
        previous = current
    return previous[-1]


def _match_score(query_word, product_words, name_count):
    best = 0
    for option in _expand(query_word):
        for index, word in enumerate(product_words):
            allowance = _allowance(option, word)
            in_name = index < name_count
            exact = 12 if in_name else 5
            partial = 8 if in_name else 3
            fuzzy = 5 if in_name else 2
            if option == word:
                best = max(best, exact)
                continue
            shorter, longer = (option, word) if len(option) <= len(word) else (word, option)
            if len(shorter) >= 3 and shorter in longer:
                best = max(best, partial)
                continue
            if len(option) >= 2 and word.startswith(option):
                best = max(best, partial)
                continue
            if (
                allowance
                and in_name
                and option[:1] == word[:1]
                and _distance(option, word, allowance) <= allowance
            ):
                best = max(best, fuzzy)
    return best


def score_product(query, name, description='', model_name=''):
    query_words = _tokens(query)
    if not query_words:
        return 0
    name_words = _tokens(f'{name or ""} {model_name or ""}')
    description_words = _tokens(description or '')
    product_words = name_words + [word for word in description_words if word not in name_words]
    if not product_words:
        return 0
    total = 0
    for word in query_words:
        matched = _match_score(word, product_words, len(name_words))
        if matched <= 0:
            return 0
        total += matched
    folded_query = ' '.join(query_words)
    folded_name = ' '.join(name_words)
    if folded_query and folded_query in folded_name:
        total += 15
    return total

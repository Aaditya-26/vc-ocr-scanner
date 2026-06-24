import re


class EntityExtractor:
    EMAIL_RE = r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}'
    MOBILE_RE = (
        r'(?:'
        r'\+?\d{1,3}[\s\-\.]?\(?\d{1,4}\)?[\s\-\.]?\d{3,5}[\s\-\.]?\d{3,5}'
        r'|'
        r'(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}'
        r')'
    )
    WEBSITE_RE = (
        r'(?:https?://)?'
        r'(?:www\.)?'
        r'[\w-]{2,}'
        r'\.'
        r'(?:com|in|org|net|io|co|biz|info|edu|gov|us|uk|au|de|fr)'
        r'(?:/\S*)?'
    )
    DESIGNATION_KEYWORDS = [
        'director', 'manager', 'engineer', 'developer', 'analyst',
        'consultant', 'founder', 'ceo', 'cto', 'coo', 'vp', 'head',
        'officer', 'executive', 'president', 'associate', 'specialist',
        'architect', 'lead', 'senior', 'junior', 'intern', 'bdm',
        'designer', 'sales', 'marketing', 'account', 'partner',
        'proprietor', 'owner', 'chairman', 'md', 'gm', 'agm',
    ]
    COMPANY_KEYWORDS = [
        'pvt', 'ltd', 'inc', 'llp', 'corp', 'technologies', 'solutions',
        'services', 'systems', 'group', 'enterprises', 'consulting',
        'software', 'tech', 'global', 'infotech', 'digital', 'company',
        'companyname',
    ]
    ADDRESS_KEYWORDS = [
        'street', 'road', 'nagar', 'colony', 'sector', 'plot', 'flat',
        'floor', 'near', 'opp', 'behind', 'mumbai', 'delhi', 'bangalore',
        'hyderabad', 'chennai', 'pune', 'kolkata', 'ahmedabad', 'pin',
        'thane', 'mall', 'agra', 'rd', '3b',
        'avenue', 'ave', 'blvd', 'lane', 'ln', 'drive', 'dr', 'court',
        'ct', 'place', 'pl', 'suite', 'ste', 'california', 'texas',
        'florida', 'york', 'london', 'ontario', 'vallejo', 'lorem',
        'ipsum', 'big', 'city', 'state', 'zip', 'po box',
    ]
    _NAME_BLOCKLIST = [
        'lets', 'make', 'work', 'simple', 'microlan', 'services',
        'pvt', 'ltd', 'it', 'support', 'www', 'http', 'slogan',
        'here', 'companyname', 'tagline', 'yourwebsite', 'domain',
    ]

    def __init__(self, text: str):
        self.text = text
        self.lines = [l.strip() for l in text.splitlines() if l.strip()]

    def extract(self) -> dict:
        email = self._get_first(self.EMAIL_RE)
        mobile = self._clean_mobile(self._get_first(self.MOBILE_RE))
        website = self._get_website(email)
        return {
            'name': self._get_name(),
            'email': email,
            'mobile': mobile,
            'website': website,
            'designation': self._get_designation(),
            'company': self._get_company(),
            'address': self._get_address(),
        }

    # ── helpers ──────────────────────────────────────────────────────────────
    def _get_first(self, pattern):
        m = re.search(pattern, self.text, re.IGNORECASE)
        return m.group(0).strip() if m else None

    def _clean_mobile(self, mobile):
        if not mobile:
            return None
        cleaned = re.sub(r'[\s\-\(\)\.]', '', mobile)
        digits = re.sub(r'\D', '', cleaned)
        return cleaned if len(digits) >= 7 else None

    def _get_website(self, email):
        """Pick the first URL-looking token that isn't the email address."""
        for m in re.finditer(self.WEBSITE_RE, self.text, re.IGNORECASE):
            candidate = m.group(0).strip()
            if email and re.sub(r'.*@', '', email) in candidate and 'www' not in candidate:
                continue
            if re.fullmatch(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', candidate):
                continue
            return candidate
        return None

    def _get_name(self):
        skip_re = re.compile(
            self.EMAIL_RE + '|' + self.MOBILE_RE + '|' + self.WEBSITE_RE,
            re.IGNORECASE,
        )
        for line in self.lines:
            if skip_re.search(line):
                continue
            words = line.split()
            if not (1 <= len(words) <= 5) or len(line) <= 2:
                continue
            lower = line.lower()
            if any(k in lower for k in self.COMPANY_KEYWORDS + self.ADDRESS_KEYWORDS):
                continue
            if any(w.lower() in self._NAME_BLOCKLIST for w in words):
                continue
            # Must be mostly alphabetic
            alpha_ratio = sum(c.isalpha() for c in line) / max(len(line), 1)
            if alpha_ratio < 0.6:
                continue
            return line
        return self.lines[0] if self.lines else 'Unknown'

    def _get_designation(self):
        for line in self.lines:
            if any(k in line.lower() for k in self.DESIGNATION_KEYWORDS):
                return line
        return None

    def _get_company(self):
        for line in self.lines:
            if any(k in line.lower() for k in self.COMPANY_KEYWORDS):
                return line
        return None

    def _get_address(self):
        addr_parts = []
        for line in self.lines:
            if any(k in line.lower() for k in self.ADDRESS_KEYWORDS):
                addr_parts.append(line)
        return ', '.join(addr_parts) if addr_parts else None

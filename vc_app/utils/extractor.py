import re


class EntityExtractor:
    EMAIL_RE = r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}'
    MOBILE_RE = r'(?:\+91[\s-]?)?[6-9]\d{9}'
    WEBSITE_RE = r'(?:https?://)?(?:www\.)\S+'

    DESIGNATION_KEYWORDS = [
        'director', 'manager', 'engineer', 'developer', 'analyst',
        'consultant', 'founder', 'ceo', 'cto', 'coo', 'vp', 'head',
        'officer', 'executive', 'president', 'associate', 'specialist',
        'architect', 'lead', 'senior', 'junior', 'intern',
    ]
    COMPANY_KEYWORDS = [
        'pvt', 'ltd', 'inc', 'llp', 'corp', 'technologies', 'solutions',
        'services', 'systems', 'group', 'enterprises', 'consulting',
        'software', 'tech', 'global', 'infotech', 'digital',
    ]
    ADDRESS_KEYWORDS = [
        'street', 'road', 'nagar', 'colony', 'sector', 'plot', 'flat',
        'floor', 'near', 'opp', 'behind', 'mumbai', 'delhi', 'bangalore',
        'hyderabad', 'chennai', 'pune', 'kolkata', 'ahmedabad', 'pin',
    ]

    def __init__(self, text: str):
        self.text = text
        self.lines = [l.strip() for l in text.splitlines() if l.strip()]

    def extract(self) -> dict:
        return {
            'name': self._get_name(),
            'email': self._get_first(self.EMAIL_RE),
            'mobile': self._clean_mobile(self._get_first(self.MOBILE_RE)),
            'website': self._get_first(self.WEBSITE_RE),
            'designation': self._get_designation(),
            'company': self._get_company(),
            'address': self._get_address(),
        }

    def _get_first(self, pattern):
        m = re.search(pattern, self.text, re.IGNORECASE)
        return m.group(0).strip() if m else None

    def _clean_mobile(self, mobile):
        if not mobile:
            return None
        return re.sub(r'[\s\-\(\)]', '', mobile)

    def _get_name(self):
        # The name is usually the first short line that is not an email/mobile/website
        skip = re.compile(
            self.EMAIL_RE + '|' + self.MOBILE_RE + '|' + self.WEBSITE_RE,
            re.IGNORECASE
        )
        for line in self.lines:
            if skip.search(line):
                continue
            words = line.split()
            # Name: 1-5 words, mostly alphabetic, not a known keyword line
            if 1 <= len(words) <= 5 and len(line) > 2:
                if not any(k in line.lower() for k in self.COMPANY_KEYWORDS + self.ADDRESS_KEYWORDS):
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

# Common Shona words for basic language detection
SHONA_MARKERS = [
    "ndiri", "ndi", "iri", "ane", "aka", "kuti", "kana", "asi",
    "uye", "zvino", "zvakanaka", "mhoro", "maswera", "ndatenda",
    "zvaita", "munhu", "vanhu", "mwana", "baba", "amai", "mhuri",
    "nyika", "musha", "mvura", "zuva", "usiku", "mangwana", "nhasi",
    "chii", "sei", "iko", "apa", "uko", "iwe", "isu", "imi", "ivo"
]

def is_shona(text: str) -> bool:
    if not text or len(text.strip()) < 3:
        return False
    words = text.lower().split()
    matches = sum(1 for word in words if any(marker in word for marker in SHONA_MARKERS))
    return matches >= 1 or len(words) <= 3  # short inputs get benefit of doubt

SHONA_ONLY_RESPONSE = (
    "Ndapota taura neni muChiShona chete. "
    "Ruzivo inoshanda muChiShona chete. Ndapota ngatishandisei Shona mukutaura kwedu"
    "Ndine hurombo, handikwanisi kudaira neumwe mutauro kunze kweShona."
)

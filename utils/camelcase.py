import re

def to_camel(s: str) -> str:
  s = s[0].lower() + s[1:] if s and s[0].isupper() else s
  return re.sub(r'_([a-zA-Z])', lambda m: m.group(1).upper(), s)

def dict_to_camel(d: dict) -> dict:
  return {to_camel(k): v for k, v in d.items()}

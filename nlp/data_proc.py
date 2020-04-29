PUNC_CHARS = "!\"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~"

# remove I, I'm from start
def rmPersonalPrefix(s):
	s = remove_prefix(s, "im ")
	s = remove_prefix(s, "i ")
	return s

# remove prefix from string
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

# remove punctuation from string
def stripPunctuation(s):
	for c in PUNC_CHARS:
		s = s.replace(c, "")
	s = s.replace("/", " ")
	return s

# to lower
def stripCaps(s):
	return s.lower()
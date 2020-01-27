PUNC_CHARS = "\'\"?!:;@.,"

# remove I, I'm from start
def rmPersonalPrefix(s):
	s = remove_prefix(s, "im ")
	s = remove_prefix(s, "i ")
	return s

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def stripPunctuation(s):
	for c in PUNC_CHARS:
		s = s.replace(c, "")
	s = s.replace("/", " ")
	return s

def stripCaps(s):
	return s.lower()
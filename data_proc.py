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

def countPunctuation(s):
	numPunc = 0
	for c in s:
		if c in PUNC_CHARS:
			numPunc += 1
	return numPunc

def stripPunctuation(s):
	for c in PUNC_CHARS:
		s = s.replace(c, "")
	s = s.replace("/", " ")
	return s

def countCaps(s):
	return sum(1 for c in s if c.isupper())

def stripCaps(s):
	return s.lower()
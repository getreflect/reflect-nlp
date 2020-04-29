import string

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
	for c in string.punctuation:
		s = s.replace(c, "")
	print(s)
	return s

# to lower
def stripCaps(s):
	return s.lower()
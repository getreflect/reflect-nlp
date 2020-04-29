import string
import random
from nltk.corpus import wordnet

stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn']

contractions = {
	"im": "i am",
	"ill": "i will",
	"dont": "do not",
	"havent": "have not",
	"doesnt": "does not",
	"he'll": "he will",
	"she'll": "she will"	
}

# remove punctuation from string
def stripPunctuation(s):
	for c in string.punctuation:
		s = s.replace(c, "")
	print(s)
	return s

# to lower
def stripCaps(s):
	return s.lower()

def stripStopWords(s):
	a = s.split(" ")
	return " ".join([w for w in a if w not in stop_words])

# stem words (maybe)

# augmentation
# using similar word2vec words
	# insert aug
	# sub aug

def synonyms(word, top_k):
	synsets = wordnet.synsets(word)

	if not synsets:
		return []

	word_synset = synsets[0]

	seen = set()
	synonyms = []
	for syn in synsets[1:]:
		for l in syn.lemmas():
			similarity = word_synset.path_similarity(syn)
			if similarity is not None and l.name() not in seen:
				seen.add(l.name())
				synonyms.append((l.name(), similarity))
	return list(synonyms)[:top_k]

def getVariations(sentence, num, mutationprob = 0.25):
	res = set()
	for n in range(num):
		words = sentence.split(" ")

		for i in range(len(words)):
			if random.uniform(0, 1) <= mutationprob:
				synsets = synonyms(words[i], 3)
				if not synsets:
					continue
				synset = random.choice(synsets)[0]
				words[i] = synset.replace("_", " ")

		res.add(" ".join(words))
	return list(res)

def expanContractions(sentence):
	words = sentence.split(" ")

	res = ""
	for w in words:
		if w in contractions:
			res += contractions[w]
		else:
			res += w
		res += " "
	return res[:-1]

# call after expanding contractions
# lower case, and stopword removal
def negation(sentence):
	if "not" in sentence:
		sentence = setence.replace("not", "")
		return sentence.replace("  ", " ")

	return "not " + sentence

def randShuffle(sentence):
	w = sentence.split(" ")
	random.shuffle(w)
	return " ".join(w)

def literalGarbage():
	pass

print(getVariations("trying to do some marketing work for my job", 3))
print(stripStopWords(expanContractions("im gonna go and dont do work")))
print(randShuffle("sometimes i dont feel so good mr stark"))
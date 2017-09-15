import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import json

TRAINING_DATA = "./bot/training_data"
INTENT_JSON = 'intents.json'

class Bot(object):
    def __init__(self, intents):
        self.intents = intents
        self.data = pickle.load(open(TRAINING_DATA, "rb"))
        self.words = self.data['words']
        self.classes = self.data['classes']
        self.train_x = self.data['train_x']
        self.train_y = self.data['train_y']
        self.stemmer = LancasterStemmer()
        self.last_response = None
        self.model = None

    def create_model(self):
        # define model
        net = tflearn.input_data(shape=[None, len(self.train_x[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(self.train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        self.model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

    def train_model(self):
        self.model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
        self.model.save('model.tflearn')

    def load_model(self):
        self.model.load('./bot/model.tflearn')

    def picke_data(self):
        import pickle
        pickle.dump( {'words':self.words, 'classes':self.classes, 'train_x':self.train_x, 'train_y':self.train_y}, open( "training_data", "wb" ) )

    def clean_sentence(self, sentence):
        # tokenize the pattern
        sentence_words = nltk.word_tokenize(sentence)
        # stem each word
        sentence_words = [self.stemmer.stem(word.lower()) for word in sentence_words]
        return sentence_words

    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def bow(self, sentence, words):
        # tokenize the pattern
        sentence_words = self.clean_sentence(sentence)
        # bag of words
        bag = [0] * len(words)
        for s in sentence_words:
            for i, word in enumerate(words):
                if word == s:
                    bag[i] = 1
        return(np.array(bag))

    def classify(self, query):
        """Classify a query/sentence.
        return: tuple (intent, probability)
        """
        error_threshold = 0.25
        # get probabilities from model
        results = self.model.predict([self.bow(query, self.words)])[0]
        # filter out predictions below threshold
        results = [[i,r] for i,r in enumerate(results) if r > error_threshold]
        results.sort(key=lambda x: x[1], reverse=True)

        classified = []
        for r in results:
            classified.append((self.classes[r[0]], r[1]))

        return classified

    def response(self, query):
        results = self.classify(query)
        # if we have a classification then find the matching intent tag
        if not results:
            return
        while results:
            for i in self.intents['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # a random response from the intent
                    response = random.choice(i['responses'])
                    if self.last_response:
                        while self.last_response == response:
                            response = random.choice(i['responses'])
                        self.last_response = response
                        return response
                    else:
                        self.last_response = response
                        return response
            results.pop(0)

    def parse_intents():
        words = []
        classes = []
        documents = []
        ignore_words = ['?']
        # loop through each sentence in our intents patterns
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                # tokenize each word in the sentence
                w = nltk.word_tokenize(pattern)
                # add to our words list
                words.extend(w)
                # add to documents in our corpus
                documents.append((w, intent['tag']))
                # add to our classes list
                if intent['tag'] not in classes:
                    classes.append(intent['tag'])

        # stem and lower each word and remove duplicates
        words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
        words = sorted(list(set(words)))

        # remove duplicates
        classes = sorted(list(set(classes)))

        print (len(documents), "documents")
        print (len(classes), "classes", classes)
        print (len(words), "unique stemmed words", words)
        return words, classes, documents

    def training_data(words, classes, documents):
        # create our training data
        training = []
        output = []
        # create an empty array for our output
        output_empty = [0] * len(classes)

        # training set, bag of words for each sentence
        for doc in documents:
            # initialize our bag of words
            bag = []
            # list of tokenized words for the pattern
            pattern_words = doc[0]
            # stem each word
            pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
            # create our bag of words array
            for w in words:
                bag.append(1) if w in pattern_words else bag.append(0)

            # output is a '0' for each tag and '1' for current tag
            output_row = list(output_empty)
            output_row[classes.index(doc[1])] = 1

            training.append([bag, output_row])

        # shuffle our features and turn into np.array
        random.shuffle(training)
        training = np.array(training)

        # create train and test lists
        train_x = list(training[:,0])
        train_y = list(training[:,1])

        return train_x, train_y



def load_intents():
    with open(INTENT_JSON) as json_data:
        return json.load(json_data)

def main():
    intents = load_intents()
    bot = Bot(intents)
    bot.create_model()
    bot.load_model()

    print(bot.response('what do you like?'))
    print(bot.response('what do you like?'))
    print(bot.response('what can i ask?'))
    print(bot.response('what can i ask?'))
    print(bot.response('why tesla?'))
    print(bot.response('why tesla?'))
    print(bot.response('what person are you'))
    print(bot.response('what person are you'))

if __name__ == '__main__':
    main()

# NL Conversational ChatServer Bot 🤖🔥
This is a project that tries to play around with the power of a very simple NL engine, defined as a
feedforward (fully connected) neural network in Tensorflow, using softmax activation with a regression in the end. So, we're basically transforming the NL problem into an intent classification problem. Cool, right?

This project has a 'bot' in its engine, and uses Flask for exposing an API through /chat for interacting with the bot. Currently, you're able to tell the bot what mood you're in, what your favourite emoji is (and store it by doing so in a small SQL DB), and ask the bot what your favourite emoji is.

## Requirements
💻 Computer
🐍 Python
🦄 APIs in requirements.txt

This project contains:
## Bot
A conversational 'bot', trained on data defined in intents.json. Able to infer the intent of a sentence/conversation and reply in a manner you define.

## Model + Training
There's a trained model in the /bot catalog.
If you want to train again with new data, run training in
```bot.py``` by executing ```python bot.py```

## How to Run
Run ```python chatserver.py``` in a terminal window for creating the server.
Run ```python client.py``` to enter chatroom and start chatting.

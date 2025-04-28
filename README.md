# A minimal turing test UI

A simple Gradio interface to run a Turing Test on your friends.

**You need:**
- An OpenAI API key
- Yourself (the judge)
- A friend
- An LLM

How it works:
- The judge asks a question like "describe a childhood memory"
- The human privately answers the question.
- The LLM answers the question.
- Judge is given both responses, anonymized, and must guess which is the human.

## Installation

Requirements:
- Python 3.9+
- OpenAI API key

```
git clone https://github.com/patrickmcrawley/turing-test.git
python3 -m venv venv
pip install -r requirements.txt
python3 main.py
```

After running, navigate to the local URL the console spits out and play.

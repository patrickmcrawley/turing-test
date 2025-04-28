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

Play around with the system prompt a bit (located at sysprompt.txt). The main problem is getting the model out of that overly yappy, corporate RLHF-pleasing tone and talking like a regular human. Once you get the model and prompt combo right, it can actually get challenging depending on the prompt. There are a couple prompt ideas in prompt_ideas.txt. I just asked o3 for a few ideas, there's probably so many cooler places to go with this, but I just threw this together with Gemini in <10 mins so I can show someone the Turing Test.

## Installation

Requirements:
- Python 3.9+
- OpenAI API key

```
git clone https://github.com/patrickmcrawley/turing-test.git
cd turing-test
python3 -m venv venv
pip install -r requirements.txt
python3 main.py
```

Next, create a .env file in the root directory of the project.
Add the following:
`OPENAI_API_KEY=sk-0000000000000000`

Replace the key with your API key, obv. 

After running, navigate to the local URL the console spits out and play.

"""
quick turing‑test harness.
roles:
  - judge (you)
  - participant 1: the LLM (edit ask_llm() as needed)
  - participant 2: the human (your lady)

how it works
-------------
1. judge types a question.
2. script fetches an answer from the LLM.
3. script prompts the human for her answer.
4. answers are anonymised and shown back to the judge as A/B.
5. judge guesses which label is the human.

quit any time by typing Ctrl‑C or entering "exit".

requirements:  Python 3.9+,  `pip install openai`.
needs `OPENAI_API_KEY` in .env file 
"""

import os
import random
import sys
import openai
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    sys.exit("Set the OPENAI_API_KEY environment variable first.")

def ask_llm(prompt: str, model: str = "gpt-4o") -> str:
    try:
        if not os.path.exists("sysprompt.txt"):
             print("Warning: sysprompt.txt not found. Creating a default one.")
             with open("sysprompt.txt", "w") as f:
                 f.write("you are being tested to see if you are human or an LLM. try to act as human as possible.")
        
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": open("sysprompt.txt").read()},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling LLM: {e}") 
        return f"Error communicating with the LLM. Please check API key and model access. Details: {e}"


def ask_human(prompt: str) -> str:
    print(f"\n[To human] {prompt}")
    return input("Human answer> ").strip()


def one_round():
    question = input("\nJudge, type your question> ").strip()
    if question.lower() in {"exit", "quit"}:
        raise KeyboardInterrupt

    llm_answer = ask_llm(question)
    human_answer = ask_human(question)

    bundles = [("Human", human_answer), ("LLM", llm_answer)]
    print(f"DEBUG: Before shuffle: {bundles}")  
    random.shuffle(bundles)
    print(f"DEBUG: After shuffle: {bundles}")  
    labels = ["A", "B"]

    print("\n" * 50)  
    print("\n---- Answers ----")
    mapping = {}
    for label, (kind, answer) in zip(labels, bundles):
        mapping[label] = kind
        print(f"{label}: {answer}\n")

    guess = input("Who was the human? [A/B]> ").strip().upper()
    if guess not in mapping:
        print("Invalid guess.")
    elif mapping[guess] == "Human":
        print("Correct")
    else:
        human_label = next(l for l, k in mapping.items() if k == "Human")
        print(f"Wrong. Human was {human_label}")
    print("------------------")


def main():
    print("Turing‑test harness ready. Ctrl‑C or type 'exit' to quit.")
    try:
        while True:
            one_round()
    except KeyboardInterrupt:
        print("\nBye.")


def process_question(question):
    if not question or not question.strip():
        return {
            human_input_group: gr.update(visible=False),
            judge_guess_group: gr.update(visible=False),
            results_output: gr.update(value="Please enter a question.", visible=True),
            llm_answer_state: "",
            question_state: "",
        }
    
    llm_answer = ask_llm(question.strip())
    return {
        llm_answer_state: llm_answer,
        question_state: question.strip(),
        human_input_group: gr.update(visible=True), 
        judge_guess_group: gr.update(visible=False), 
        results_output: gr.update(value=f"LLM answered. Now enter the human's answer to the question below.", visible=True),
        judge_question_textbox: gr.update(interactive=False),
        submit_question_button: gr.update(interactive=False),
        human_answer_textbox: gr.update(value="", placeholder=f"Human's answer to: {question.strip()}"), # Clear and set placeholder
    }


def process_human_answer(human_answer, question, llm_answer):
    if not human_answer or not human_answer.strip():
        return {
            judge_guess_group: gr.update(visible=False),
            results_output: gr.update(value="Please enter the human's answer.", visible=True),
            answer_A_textbox: "",
            answer_B_textbox: "",
            mapping_state: {},
        }

    bundles = [("Human", human_answer.strip()), ("LLM", llm_answer)] 
    random.shuffle(bundles)
    labels = ["A", "B"]
    mapping = {}
    answer_a_text = ""
    answer_b_text = ""

    for label, (kind, answer) in zip(labels, bundles):
        mapping[label] = kind
        if label == "A":
            answer_a_text = answer
        else:
            answer_b_text = answer

    return {
        answer_A_textbox: answer_a_text,
        answer_B_textbox: answer_b_text,
        mapping_state: mapping,
        judge_guess_group: gr.update(visible=True), 
        human_input_group: gr.update(visible=False),
        results_output: gr.update(value=f"""Answers received for:
'{question}'

Judge, who is the human?""", visible=True), 
        guess_radio: gr.update(value=None) 
    }


def process_guess(guess, mapping, question):
    if not guess:
        return {results_output: gr.update(value="Please select A or B to make your guess.")}

    result_text = ""
    correct = False
    if mapping.get(guess) == "Human":
        result_text = f"Correct! '{guess}' was the Human."
        correct = True
    else:
        human_label = next((l for l, k in mapping.items() if k == "Human"), "?")
        result_text = f"Wrong. '{guess}' was the LLM. The Human was '{human_label}'."

    final_output = f"""Result for question: '{question}'

{result_text}

Enter a new question above to play again.""" 

    return {
         results_output: gr.update(value=final_output, visible=True),
         judge_question_textbox: gr.update(value="", interactive=True, placeholder="Enter your next question"),
         submit_question_button: gr.update(interactive=True),
         judge_guess_group: gr.update(visible=False),
         human_input_group: gr.update(visible=False),
         answer_A_textbox: "",
         answer_B_textbox: "",
         guess_radio: gr.update(value=None),
         llm_answer_state: "",
         question_state: "",
         mapping_state: {},
    }


with gr.Blocks(title="Turing Test", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Turing Test 🤖 vs 👩‍🦰")
    gr.Markdown("""
    **Instructions:**
    1.  As the **Judge**, type a question and click **Submit Question**.
    2.  The LLM will generate an answer in the background.
    3.  Ask your **Human** participant the *same* question. Type their exact answer into the **Human's Answer** box and click **Show A/B Answers**.
    4.  You will see two answers labeled **A** and **B** (randomized).
    5.  Select **A** or **B** based on which you believe is the Human's answer, then click **Submit Guess**.
    """)

    llm_answer_state = gr.State("")
    question_state = gr.State("")
    mapping_state = gr.State({})

    with gr.Column():
        with gr.Row():
            judge_question_textbox = gr.Textbox(
                label="1. Judge: Enter your question",
                placeholder="e.g., What is the meaning of life?",
                lines=2,
                scale=4
            )
            submit_question_button = gr.Button("Submit Question", variant="primary", scale=1)

        with gr.Group(visible=False) as human_input_group:
             with gr.Row():
                human_answer_textbox = gr.Textbox(
                    label="2. Judge: Enter the HUMAN's answer",
                    placeholder="Waiting for question...",
                    lines=2,
                    scale=4
                )
                submit_human_answer_button = gr.Button("Show A/B Answers", variant="secondary", scale=1)


        with gr.Group(visible=False) as judge_guess_group:
            gr.Markdown("### 3. Judge: Review Answers A & B")
            with gr.Row():
                answer_A_textbox = gr.Textbox(label="Answer A", interactive=False, lines=3)
                answer_B_textbox = gr.Textbox(label="Answer B", interactive=False, lines=3)
            with gr.Row():
                guess_radio = gr.Radio(["A", "B"], label="Which answer is from the Human?", scale=3)
                submit_guess_button = gr.Button("Submit Guess", variant="primary", scale=1)

        results_output = gr.Markdown(value="Enter a question to begin.", visible=True)


    submit_question_button.click(
        fn=process_question,
        inputs=[judge_question_textbox],
        outputs=[
            llm_answer_state,
            question_state,
            human_input_group,
            judge_guess_group,
            results_output,
            judge_question_textbox,
            submit_question_button,
            human_answer_textbox,
        ]
    )

    submit_human_answer_button.click(
        fn=process_human_answer,
        inputs=[human_answer_textbox, question_state, llm_answer_state],
        outputs=[
            answer_A_textbox,
            answer_B_textbox,
            mapping_state,
            judge_guess_group,
            human_input_group,
            results_output,
            guess_radio
        ]
    )

    submit_guess_button.click(
        fn=process_guess,
        inputs=[guess_radio, mapping_state, question_state],
        outputs=[
            results_output,
            judge_question_textbox,
            submit_question_button,
            judge_guess_group,
            human_input_group,
            answer_A_textbox,
            answer_B_textbox,
            guess_radio,
            llm_answer_state,
            question_state,
            mapping_state,
        ]
    )

if __name__ == "__main__":
    print("Turing‑test harness ready. Launching Gradio interface...")
    print("Ensure your OPENAI_API_KEY is set in a .env file or environment variables.")

    demo.launch()

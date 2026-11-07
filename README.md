# The All-in-One Agentic AI Evergreen System — Code Repository

The finished, tested code of the book *The All-in-One Agentic AI Evergreen System* by Isaac Vance, organized stage by stage. Every folder matches a stage of the book. Read the decisions in the book first, then come here for the code: nothing to retype.

## How to use it

1. **Download the code.** Click the green **Code** button above and choose **Download ZIP**, or clone it with Git:

   ```
   git clone https://github.com/BookBurst/agentic-ai-evergreen-system.git
   ```

2. **Open the folder of the stage you're working on**, for example `stage-02`, and work inside it from the terminal with `cd`.

3. **Create your virtual environment, activate it and install the package**, as shown in Stage 2:

   ```
   python -m venv .venv
   Windows:      .venv\Scripts\activate
   Mac / Linux:  source .venv/bin/activate
   python -m pip install openai
   ```

   A few stages need one more package, and the book tells you when: `pillow` (Stage 3, the receipt), `mcp` (Stage 3, the tool server) and `tiktoken` (Stage 8, counting tokens).

4. **Create your `.env` file** in the same folder. Copy `stage-02/.env.example`, rename it `.env` and fill in your own values:

   ```
   API_KEY=paste-your-key-here
   MODEL_NAME=the-model-name-your-provider-lists
   BASE_URL=
   ```

5. **Read the code line by line, then run it.** Ask a chat assistant about any line you don't follow.

**Never upload your `.env` file and never paste your API key into a chat.** The `.gitignore` in this repository already keeps `.env` out of Git. If a key ever leaks, delete it in your provider's dashboard and create a new one.

## What's inside

| Folder | Stage |
|---|---|
| `stage-02` | Your First AI Agent, Built from Scratch |
| `stage-03` | Answers with Sources, Not Confident Guesses |
| `stage-04` | The 24/7 Setup, Your Agent Always Ready at Home |
| `stage-05` | From One Agent to Your AI Agent Team |
| `stage-06` | From Confusion to a Clear Map |
| `stage-07` | Agents That Catch Their Own Mistakes |
| `stage-08` | Every Token Counted, Agent by Agent |
| `stage-09` | Costs You Can See and Cap |
| `stage-10` | The Agentic Development Lifecycle (ADLC) and Automatic Checks |
| `stage-11` | Security and Data Privacy |
| `stage-12` | Trust and Accountability |

Stage 1 is about the ideas behind every agent and has no code to run.

The files in `notes`, `docs`, `inbox` and `sources` are made-up examples for a first test. Replace them with your own files when you're ready.

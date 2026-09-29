Getting your Voyage API key
Today's work needs a second API key, separate from your Anthropic one. Voyage is a different company that provides the embedding model we are using. Your Anthropic key will not work here, you need a new one from Voyage directly.

Step 1: create an account
Go to: https://dashboard.voyageai.com
Sign up with your email. No payment details are needed to get started.

Step 2: get your key
Once you are logged in, look for a section called API Keys. Create a new key, give it a name if asked, and copy it straight away. Some dashboards only show you the full key once, so copy it before navigating away.

Step 3: set it in your terminal
Same pattern as your Anthropic key. In Git Bash:

bash
```
export VOYAGE_API_KEY="pa-..."Paste your real key in place of pa-....
```
This only lasts for the terminal window you typed it into. If you close the window or open a new one, you will need to set it again.
Step 4: check it worked

```
.venv/bin/python -c "import os; print('voyage key present:', bool(os.environ.get('VOYAGE_API_KEY')))"You should see voyage key present: True.
```

NOTE: new Voyage accounts come with free tokens for testing, so you will not be charged for anything we do today.

then, install package:
```
.venv/bin/python -m pip install voyageai
```
```
.venv/bin/python -c "import knowledge; print('client ready, model =', knowledge.EMBED_MODEL)"
```
```
import knowlege
```
```
vectors, tokens = knowledge.embed_texts(["Okonkwo Bell works in energy"], "document")
```
```
print("dimensions:", len(vectors[0]))
print("first five:", vectors[0][:5])
print("tokens:", tokens)
```
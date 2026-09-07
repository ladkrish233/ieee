# IEEE Paper Generator

FastAPI app that generates IEEE-formatted research paper drafts (.docx) using AI agents.

**Live app:** https://ieee-production.up.railway.app

## Local setup

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Requires an `ANTHROPIC_API_KEY` in a `.env` file.

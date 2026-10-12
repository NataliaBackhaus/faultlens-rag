# FaultLens RAG: multimodal troubleshooting for solar installers

**Multimodal RAG copilot that diagnoses solar inverter error codes from technical manuals, and cites the page.**

An installer types a model and an error code; FaultLens RAG returns the diagnosis, likely causes, the fix and the exact manual page, including answers hidden in wiring diagrams and LED charts. Answers are filtered by model and firmware, so a fix for one inverter is never served for another.

- v1: SMA and Fronius inverters (English manuals)
- v2: Viessmann heat pumps
- 100% free and open-source stack: Docling, Qwen2.5-VL via Ollama, Qdrant, FastEmbed, FastAPI, Streamlit, Ragas, Arize Phoenix

Status: in development. Results, architecture diagram and demo video will appear here as the sprints land.

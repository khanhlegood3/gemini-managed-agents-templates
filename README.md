# Gemini Managed Agents Templates

This repository contains a collection of templates for building and deploying Gemini Managed Agents using the Gemini API. These templates demonstrate the power of the Gemini API sandbox, including code execution, filesystem operations, and web search.

## Available Templates

- **Data Analyst**: Upload a CSV and get full data analysis with charts and insights.
- **AI Radio**: Turn today's top Hacker News stories into a radio program (podcast briefing).
- **Repo Maintainer**: Provide a GitHub repo URL, find top issues, fix them, and send Pull Requests.
- **Document Processor**: A template for processing and analyzing documents.
- **News Curator**: Personalized daily briefings on a Trigger schedule — sweeps Google News, Hacker News, and Medium for your topics, learns your taste across runs via the persistent environment.
- **SEO Auditor**: Audit published web apps for loading speed, Core Web Vitals, mobile usability, and search readiness using Lighthouse and Google Search.


## Getting Started

To use these templates, you can reference them in your Gemini API calls or use the Gemini API CLI to scaffold new agents based on these templates.

## Static site and GitHub Actions

The static catalog is built from the template `agent.yaml` files and deployed to [GitHub Pages](https://khanhlegood3.github.io/gemini-managed-agents-templates/) on pushes to `main`. Pull requests build and test the site without deploying. In repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**. A manual Pages run deploys only when run from `main`.

To build locally (Python 3.9+):

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install 'PyYAML==6.0.3'
python scripts/build_site.py
python -m unittest discover -s tests -v
python -m http.server --directory _site 8000
```

The nightly workflow validates templates and payload generation on pull requests without accessing secrets or making API calls. Scheduled and manually triggered live probes require the `GEMINI_API_KEY` repository Actions secret. Live probes can incur API usage and require access to the configured agent and Gemini Interactions API. If the key is missing, the workflow fails once during setup with instructions instead of creating one failure per prompt. Probe issues are managed only when repository Issues are enabled; the Actions token must have permission to write issues. Failed probes are retried three times; pending issues are promoted after a subsequent failure at least two hours later.

## Running Probers

Each template directory contains a `probers.sh` script that can be used to test the agent template by sending a "Hello" prompt to the Gemini API. These probers read the template information (like `AGENTS.md` and skills) dynamically from disk.

To run a prober:

1.  Set your `GEMINI_API_KEY` environment variable:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```

2.  Navigate to the template directory you want to test (e.g., `data-analyst`):
    ```bash
    cd data-analyst
    ```

3.  Run the prober script:
    ```bash
    ./probers.sh
    ```

The script will call `../generate_payload.py` to construct the payload dynamically and then use `curl` to make the API request.


## Licensing & Disclaimer

Copyright 2026 Google LLC  

All software is licensed under the Apache License, Version 2.0 (Apache 2.0); you may not use this file except in compliance with the Apache 2.0 license. You may obtain a copy of the Apache 2.0 license at: [https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)

All other materials are licensed under the Creative Commons Attribution 4.0 International License (CC-BY). You may obtain a copy of the CC-BY license at: [https://creativecommons.org/licenses/by/4.0/legalcode](https://creativecommons.org/licenses/by/4.0/legalcode)

Unless required by applicable law or agreed to in writing, all software and materials distributed here under the Apache 2.0 or CC-BY licenses are distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the licenses for the specific language governing permissions and limitations under those licenses.

This is not an official Google product.

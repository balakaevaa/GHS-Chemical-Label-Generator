# GHS Chemical Label Generator

A lightweight web application for generating standardized, print-ready GHS/CLP chemical safety labels by CAS registry number.

## Features
- **Automated Data Retrieval**: Fetches official GHS classifications, hazard pictograms, H-statements, and P-statements directly from PubChem PUG-REST API.
- **Offline Pictogram Support**: Embedded standalone SVG GHS hazard pictograms (GHS01–GHS09).
- **High-Resolution Export**: Export labels directly to 300 DPI PNG / JPG or browser-based vector PDF printing.
- **Local Caching**: Asynchronous SQLite caching to minimize external API requests.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn, HTTPX, aiosqlite
- **Frontend / Rendering**: Jinja2, HTML5/CSS Print (@page 100x70 mm), html2canvas

## Quick Start

1. Clone repository:
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/ghs-label-generator.git
   cd ghs-label-generator


# SDP Explorer - Claude Code Documentation

This directory contains Claude Code configuration and documentation for the SDP Explorer project.

## Project Overview
SDP Explorer is a Flask-based web application for exploring and interacting with the ManageEngine Service Desk Plus API.

## Quick Start
- Main application: `app.py`
- Configuration: `config.py`
- Frontend: `static/explorer.js` and `templates/`
- Full project documentation: See `claude.md` in root directory

## Key Files
- `app.py:12-57` - API call handler
- `app.py:64-76` - Connection test endpoint
- `config.py` - API configuration and endpoints
- `static/explorer.js:455-740` - Smart response renderer
- `static/explorer.js:195-295` - Dynamic field discovery

## Running the Application
```bash
pip install -r requirements.txt
python app.py
```

Access at: http://127.0.0.1:5000

## Architecture
- **Backend**: Flask 3.0.0
- **API**: ManageEngine Service Desk Plus v3 REST API
- **Frontend**: Vanilla JavaScript

For detailed documentation, refer to `claude.md` in the project root.

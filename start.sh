#!/bin/bash

# Open gnome-terminal with two tabs
# First tab: Backend
gnome-terminal --tab --title="Backend" -- bash -c 'source .venv/bin/activate; python -m backend.main; exec bash'

# Second tab: Frontend
gnome-terminal --tab --title="Frontend" -- bash -c 'cd frontend; npm run dev; exec bash'
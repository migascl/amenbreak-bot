# Discord Amen Break Bot

A Discord bot that posts and plays random amen breaks - with some other goofy features.

### Prerequisites

- Python 3.8 or higher
- FFMPEG

### How to setup

1. Install `python-dotenv` and `py-cord`
2. Copy the `.env.example` file, rename it to `.env` and change the values accordingly
3. The folder `assets` is where all the samples are stored.
4. Run the python script `main.py`

### Commands

- ##### `/amen` - Get a random amen break sample

  _Optional Argument_ (`type`):
  - `post` - Responds with a random audio sample.
  - `play` - Joins a voice channel and plays a random audio sample.
  - `tabs` - Responds with the amen break tabs.

- ##### `/rant` - Post a random copypasta

- ##### `/about` - Shows information about the bot

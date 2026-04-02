<p align="center">
  <img src="assets/logo.jpg" alt="Deeam Bot Logo" width="200">
</p>

<h1 align="center">Deeam Bot</h1>
<p align="center">
  A powerful Telegram auto-filter & file-search bot built with Pyrogram and MongoDB.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Pyrogram-2.0.106-green?style=flat-square" alt="Pyrogram">
  <img src="https://img.shields.io/badge/MongoDB-Motor-brightgreen?style=flat-square&logo=mongodb" alt="MongoDB">
  <img src="https://img.shields.io/badge/License-GPL--3.0-orange?style=flat-square" alt="License">
</p>

---

## Features

- **Auto-filter** — automatically replies with matching files when users type movie/series names in connected groups
- **Manual filters** — set custom keyword → response triggers per group
- **Global filters** — filters that apply across all connected groups
- **IMDb integration** — fetches movie posters, ratings, plot, cast info
- **Spell check** — suggests similar titles when an exact match isn't found
- **Shortlink support** — wraps file links through a shortlink service
- **Verification system** — optional token-based user verification before file access
- **Broadcast** — send messages to all users or groups
- **Connection system** — manage bot from PM by connecting to a group
- **Link generator** — create shareable links for single posts or batches
- **Auto-delete** — automatically deletes sent files after a set time
- **Protect content** — optional forwarding protection on sent files

---

## Deployment

### Prerequisites

- Python **3.8+**
- A [MongoDB Atlas](https://www.mongodb.com/atlas) database (free tier works)
- Telegram **API ID** and **API Hash** from [my.telegram.org](https://my.telegram.org)
- A bot token from [@BotFather](https://t.me/BotFather)

---

### Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Shubhamxd82/Dream-V2)

---

### Deploy to Koyeb

<a href="https://app.koyeb.com/deploy?type=git&repository=github.com/Shubhamxd82/Dream.upgrades__TEST&branch=master&name=deeambot">
  <img alt="Deploy to Koyeb" src="https://binbashbanana.github.io/deploy-buttons/buttons/remade/koyeb.svg">
</a>

---

### Deploy with Docker

```bash
git clone https://github.com/your-repo/deeam-bot
cd deeam-bot
cp sample_info.py info.py   # fill in your values
docker-compose up -d
```

---

### Deploy manually (VPS / local)

```bash
git clone https://github.com/your-repo/deeam-bot
cd deeam-bot
pip3 install -U -r requirements.txt
cp sample_info.py info.py   # fill in your values
python3 bot.py
```

---

## Configuration

Copy `sample_info.py` to `info.py` and fill in each value. All variables can also be set as environment variables (recommended for cloud deployments).

### Required variables

| Variable | Description |
|---|---|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `DATABASE_URI` | MongoDB connection URI (e.g. `mongodb+srv://user:pass@cluster.mongodb.net/`) |
| `DATABASE_NAME` | MongoDB database name |
| `ADMINS` | Space-separated list of admin user IDs |
| `CHANNELS` | Space-separated list of channel IDs the bot indexes files from |
| `LOG_CHANNEL` | Channel ID where bot logs events |

### Optional variables

| Variable | Default | Description |
|---|---|---|
| `COLLECTION_NAME` | `Telegram_files` | MongoDB collection name for indexed files |
| `AUTH_CHANNEL` | `None` | Force users to join this channel before using the bot |
| `AUTH_GROUP` | `None` | Restrict bot usage to specific group IDs |
| `SUPPORT_CHAT` | — | Username of your support group |
| `SUPPORT_CHAT_ID` | — | ID of your support group |
| `REQUEST_LOGS` | — | Channel ID for logging file requests |
| `REQST_CHANNEL_ID` | — | Channel ID for request forwarding |
| `LOG_CHANNEL` | — | Channel ID for general logs |
| `CACHE_TIME` | `300` | Inline query cache time in seconds |
| `USE_CAPTION_FILTER` | `False` | Search inside file captions as well as filenames |
| `MAX_B_TN` | `5` | Maximum number of file buttons shown per result |
| `MAX_BTN` | `True` | Show file size alongside file name button |
| `SINGLE_BUTTON` | `True` | Combine filename and file size into one button |
| `AUTO_FFILTER` | `True` | Enable auto-filter (auto-reply on keyword match) |
| `AUTO_DELETE` | `True` | Auto-delete sent files after 10 minutes |
| `PROTECT_CONTENT` | `False` | Enable forward protection on sent files |
| `PUBLIC_FILE_STORE` | `True` | Allow public access to file store links |
| `P_TTI_SHOW_OFF` | `True` | Redirect users to bot PM instead of sending files in group |
| `IMDB` | `False` | Show IMDb info card with results |
| `LONG_IMDB_DESCRIPTION` | `False` | Show full IMDb plot (shorter by default) |
| `IMDB_TEMPLATE` | built-in | Custom template for IMDb result messages |
| `SPELL_CHECK_REPLY` | `True` | Suggest similar titles when no results found |
| `VERIFY` | `True` | Enable token-based user verification |
| `IS_SHORTLINK` | `True` | Wrap file links through a shortlink service |
| `SHORTLINK_URL` | `tnlink.in` | Your shortlink service domain |
| `SHORTLINK_API` | — | Your shortlink service API key |
| `CUSTOM_FILE_CAPTION` | built-in | Custom caption template for sent files |
| `BATCH_FILE_CAPTION` | same as above | Caption for batch file sends |
| `BLACKLIST_WORDS` | — | Comma-separated words to strip from file names in results |
| `MAX_LIST_ELM` | `None` | Limit cast/crew list length in IMDb cards |
| `MELCOW_NEW_USERS` | `False` | Send welcome video to new users |
| `MELCOW_VID` | built-in | URL of welcome video |
| `PICS` | built-in | Space-separated image URLs for start message |
| `NOR_IMG` | built-in | Image shown when results are found |
| `SPELL_IMG` | built-in | Image shown for spell-check suggestions |
| `DELETE_CHANNELS` | — | Channel IDs — files deleted from these channels are removed from DB |
| `FILE_STORE_CHANNEL` | — | Channel IDs for storing generated file links |
| `INDEX_REQ_CHANNEL` | same as `LOG_CHANNEL` | Channel for index request notifications |
| `GRP_LNK` | — | Invite link to your main group |
| `CHNL_LNK` | — | Link to your main channel |
| `MSG_ALRT` | `Thanks To Using Me 😇` | Alert text shown on certain interactions |
| `PORT` | `8080` | Web server port (for health checks) |

---

## Bot Commands

### User commands

| Command | Description |
|---|---|
| `/start` | Start the bot / get welcome message |
| `/help` | Show help message |
| `/about` | About this bot |
| `/imdb` | Fetch IMDb info for a movie/series title |
| `/id` | Get Telegram IDs for yourself, a user, or a chat |
| `/info` | Get detailed info about a user |
| `/connect` | Connect a group to your PM for remote management |
| `/disconnect` | Disconnect from a group |
| `/filter` | Add a manual filter (keyword → response) |
| `/filters` | List all filters in the current chat |
| `/del` | Delete a specific filter |
| `/delall` | Delete all manual filters in the current chat |
| `/link` | Generate a shareable link for a single post |
| `/batch` | Generate a shareable link for a range of posts |

### Admin commands

| Command | Description |
|---|---|
| `/logs` | Get recent error logs |
| `/stats` | Show database stats (total indexed files, users, chats) |
| `/users` | List all users and their IDs |
| `/chats` | List all connected chats and their IDs |
| `/channel` | Show connected channel info |
| `/index` | Index files from a channel into the database |
| `/deleteall` | Delete all indexed files (auto-filter database) |
| `/delete` | Delete a specific file from the index |
| `/files_delete` | Bulk delete files from the index by filter |
| `/broadcast` | Broadcast a message to all users |
| `/ban` | Ban a user from using the bot |
| `/unban` | Unban a user |
| `/leave` | Make the bot leave a chat |
| `/disable` | Disable the bot in a chat |
| `/enable` | Re-enable the bot in a chat |

---

## How it works

1. **Indexing** — an admin runs `/index` pointing at a channel. The bot saves all file metadata (name, size, file ID, type) into MongoDB.
2. **Auto-filter** — when a user types a movie name in a connected group, the bot searches the index and replies with matching file buttons.
3. **File delivery** — clicking a button sends the user a PM with the file (optionally through a shortlink and/or verification step).
4. **Auto-delete** — after 10 minutes, the sent file and the result message are automatically deleted from the group.

---

## Tech stack

| Package | Version | Purpose |
|---|---|---|
| `pyrogram` | 2.0.106 | Telegram MTProto client |
| `tgcrypto` | latest | Crypto acceleration for Pyrogram |
| `motor` | 2.5.1 | Async MongoDB driver |
| `pymongo[srv]` | 3.12.3 | MongoDB connection utilities |
| `umongo` | 3.0.1 | MongoDB ODM |
| `marshmallow` | 3.14.1 | Schema serialization |
| `imdbpy` | 2022.7.9 | IMDb data fetching |
| `aiohttp` | latest | Async HTTP client (shortlinks, web scraping) |
| `bs4` | latest | HTML parsing |
| `pytz` | latest | Timezone handling |
| `datetime` | latest | Date/time utilities |

---

## License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

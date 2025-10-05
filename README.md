# Convert Your WhatsApp Partner into Character AI

This project converts your **WhatsApp chat history** with someone into structured **dialogue examples** for **Character.AI**, **chatbots**, or other conversational AI projects.
It reads your exported WhatsApp messages, cleans them, and formats them into a ready-to-use `example_conversation.json` structure that can be pasted directly into your character definition textbox.

---

## Disclaimer

All code in this project was generated with the assistance of Claude Sonnet 3.5, an AI language model. While the code has been tested and verified to work as intended, please review it carefully for your specific use case.

---

## Project Vision

The goal of this project is to let you **bring real conversations to life** in AI characters.
By converting your chat history into realistic dialogue data, your Character.AI persona can reflect your partner’s tone, habits, and natural speaking style.

---

## Features

* **Automatic WhatsApp Chat Parsing**
  Reads `.txt` exports and extracts all messages with timestamps and senders.
* **Conversation Splitting by Time**
  Groups messages into natural conversation blocks based on gaps in time.
* **Duplicate Key-Preserving JSON**
  Keeps multiple `"{{char}}"` and `"{{random_user_1}}"` entries within the same conversation.
* **Filter or Replace Media and Links**
  Choose to remove or replace `<Media omitted>` and link messages.
* **Skip Short Conversations**
  Ignore unimportant or one-line chats using `min_messages_per_conversation`.
* **Character Limit and Random Sampling**
  Keep output under a maximum character count while still maintaining variety.

---

## Example Output

```json
{
  "example_conversation": [
    {
      "{{random_user_1}}": "Tbh I don't like drawing",
      "{{random_user_1}}": "The process, it's just",
      "{{random_user_1}}": "Sucks",
      "{{random_user_1}}": "But I liked the results",
      "{{char}}": "well as they said",
      "{{char}}": "trust the process",
      "{{char}}": "tbh I hate the process too",
      "{{char}}": "it's suck",
      "{{char}}": "that's why sometimes I'm getting stuck",
      "{{char}}": "but that's just how it is"
    },
    {
      "{{random_user_1}}": "Man, why’s your past so dark",
      "{{char}}": "yeah it's alright tho, it's already happening",
      "{{random_user_1}}": "What?? Like currently??",
      "{{char}}": "I don't freaking know why owkwkwk😭"
    }
  ]
}
```

---

## Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/yourusername/convert-your-whatsapp-partner-into-character-ai.git
   cd convert-your-whatsapp-partner-into-character-ai
   ```

2. **Install dependencies**
   Requires Python 3.8+ and standard libraries only.

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. **Export your WhatsApp chat**

   * Open your chat in WhatsApp.
   * Tap the three dots (⋮) → **More** → **Export chat** → **Without media**.
   * Save it as `chat.txt` inside this project folder.

---

## How to Use

### Step 1: Open the Script

Open the file **`whatsapp_to_json.py`** in any text editor.

### Step 2: Choose Your Template

The project provides two JSON templates for Character.AI:

* `template.json` - Basic template for character definitions
* `example.json` - Alternative template with example structure

Both files can be used as base templates. Copy the generated `example_conversation` from `example_conversation.json` into either template file to create your character definition.

### Step 3: Scroll Down to the Example Section

Scroll to the **bottom** of the file until you find the following block:

```python
# Example usage
if __name__ == "__main__":
    generate_conversation_json(
        input_file="whatsapp_chat.txt",            # Path to your WhatsApp chat export
        output_file="example_conversation.json",   # Output JSON file
        split_minutes=15,                          # Split conversations if gap > 15 minutes
        character_limit=20000,                     # Max characters in output JSON
        filter_media=True,                         # True to remove media messages
        filter_links=True,                         # True to remove link messages
        user_name="Razanius12",                    # Your WhatsApp username
        char_name="My Partner",                    # Chat partner’s username
        min_messages_per_conversation=4,           # Minimum messages per conversation block
        media_replacement="<sends an attachment>", # Replace media (None to keep)
        link_replacement="<sends a link>"          # Replace links (None to keep)
    )
```

### Step 4: Adjust the Parameters

Edit the parameters according to your needs.
You can change:

* The input and output file names.
* Your and your partner’s usernames.
* How messages are split, filtered, or replaced.
* Minimum messages per conversation.
* Character limit for the output.

### Step 5: Run the Script

After saving your changes, run:

```bash
python whatsapp_to_json.py
# or 
py whatsapp_to_json.py

```

This generates a file called **`example_conversation.json`** in the same directory.

---

## Parameters Overview

| Parameter                       | Type        | Description                                         |
| ------------------------------- | ----------- | --------------------------------------------------- |
| `input_file`                    | str         | Path to your WhatsApp `.txt` export                 |
| `output_file`                   | str         | Name of the JSON file to be generated               |
| `split_minutes`                 | int         | Maximum time gap before starting a new conversation |
| `character_limit`               | int         | Limit total characters in final JSON                |
| `filter_media`                  | bool        | Remove messages containing `<Media omitted>`        |
| `filter_links`                  | bool        | Remove messages containing URLs                     |
| `user_name`                     | str         | Your WhatsApp display name                          |
| `char_name`                     | str         | Your chat partner’s name                            |
| `min_messages_per_conversation` | int         | Skip conversations with fewer messages              |
| `media_replacement`             | str or None | Replace `<Media omitted>` with custom text          |
| `link_replacement`              | str or None | Replace link messages with custom text              |

---

## How It Works

1. Reads and parses your WhatsApp `.txt` export.
2. Identifies senders, timestamps, and message contents.
3. Groups messages into conversation blocks by `split_minutes`.
4. Removes or replaces media and link messages.
5. Skips short or single-sender conversations.
6. Serializes data into `example_conversation.json` with duplicate key support.

---

## Troubleshooting

### 1. JSON file is empty

* Make sure `user_name` and `char_name` match the exact names in your WhatsApp export.
* Lower `min_messages_per_conversation` to include shorter chats.

### 2. Messages missing or incomplete

* Try setting `filter_media=False` and `filter_links=False`.
* Increase `character_limit` to allow more content.

### 3. Encoding errors

* Ensure the exported chat is **UTF-8 encoded**.
* Avoid editing the `.txt` manually before running the script.

### 4. Duplicate key warnings

* These are intentional. The script uses custom JSON serialization to preserve multiple `"{{char}}"` and `"{{random_user_1}}"` entries per conversation.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for bug fixes, improvements, or new features.

---

## License

See the [LICENSE](LICENSE) file for details.

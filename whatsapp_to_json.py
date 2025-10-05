import re
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import random


def parse_whatsapp_line(line: str) -> Optional[Dict[str, str]]:
    """
    Parse a single WhatsApp chat line.
    Returns dict with 'timestamp', 'username', 'message' or None if invalid.
    """
    # Pattern: "12/25/21, 12:51 PM - Username: Message"
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+[AP]M)\s+-\s+([^:]+):\s+(.*)$'
    match = re.match(pattern, line)

    if match:
        timestamp_str, username, message = match.groups()
        try:
            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, '%m/%d/%y, %I:%M %p')
            return {
                'timestamp': timestamp,
                'username': username.strip(),
                'message': message.strip()
            }
        except ValueError:
            return None
    return None


def parse_whatsapp_chat(file_path: str) -> List[Dict[str, str]]:
    """
    Parse entire WhatsApp chat file into list of messages.
    Handles multi-line messages.
    """
    messages = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_message = None

    for line in lines:
        line = line.rstrip('\n')

        # Try to parse as new message
        parsed = parse_whatsapp_line(line)

        if parsed:
            # Save previous message if exists
            if current_message:
                messages.append(current_message)
            current_message = parsed
        else:
            # Continue previous message (multi-line)
            if current_message and line.strip():
                current_message['message'] += ' ' + line.strip()

    # Add last message
    if current_message:
        messages.append(current_message)

    return messages


def contains_link(message: str) -> bool:
    """
    Check if message contains a URL.
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return bool(re.search(url_pattern, message))


def group_by_time_gap(messages: List[Dict], split_minutes: int,
                      filter_media: bool, filter_links: bool,
                      media_replacement: Optional[str],
                      link_replacement: Optional[str]) -> List[List[Dict]]:
    """
    Group messages into conversation blocks based on time gap.
    """
    if not messages:
        return []

    blocks = []
    current_block = []

    for i, msg in enumerate(messages):
        # Handle media messages
        if '<Media omitted>' in msg['message']:
            if filter_media:
                continue
            elif media_replacement:
                msg['message'] = media_replacement

        # Handle link messages
        if contains_link(msg['message']):
            if filter_links:
                continue
            elif link_replacement:
                msg['message'] = link_replacement

        # Skip empty messages
        if not msg['message'].strip():
            continue

        # Remove newlines from message
        msg['message'] = msg['message'].replace('\n', ' ').replace('\r', ' ')

        if not current_block:
            current_block.append(msg)
        else:
            # Check time difference
            time_diff = (msg['timestamp'] - current_block[-1]
                         ['timestamp']).total_seconds() / 60

            if time_diff > split_minutes:
                # Start new block
                blocks.append(current_block)
                current_block = [msg]
            else:
                current_block.append(msg)

    # Add last block
    if current_block:
        blocks.append(current_block)

    return blocks


def filter_single_speaker_blocks(blocks: List[List[Dict]], min_messages: int = 2) -> List[List[Dict]]:
    """
    Remove blocks that have only one speaker or too few messages.

    Args:
        blocks: List of conversation blocks
        min_messages: Minimum number of messages required per block
    """
    filtered = []

    for block in blocks:
        speakers = set(msg['username'] for msg in block)
        if len(speakers) >= 2 and len(block) >= min_messages:
            filtered.append(block)

    return filtered


def convert_to_json_format(blocks: List[List[Dict]], user_name: str,
                           char_name: str) -> List[List[Tuple[str, str]]]:
    """
    Convert blocks to list of (key, value) tuples to allow duplicate keys.
    """
    result = []

    for block in blocks:
        conversation = []
        speakers_present = set()

        for msg in block:
            if msg['username'] == user_name:
                key = "{{random_user_1}}"
                speakers_present.add(key)
            elif msg['username'] == char_name:
                key = "{{char}}"
                speakers_present.add(key)
            else:
                # Skip messages from unknown users
                continue

            conversation.append((key, msg['message']))

        # Only add if conversation has both speakers
        if len(speakers_present) >= 2 and conversation:
            result.append(conversation)

    return result


def serialize_to_json_with_duplicate_keys(conversations: List[List[Tuple[str, str]]]) -> str:
    """
    Custom JSON serialization that allows duplicate keys.
    """
    lines = ['{']
    lines.append('  "example_conversation": [')

    for i, conv in enumerate(conversations):
        lines.append('    {')

        for j, (key, value) in enumerate(conv):
            # Escape the value for JSON
            escaped_value = json.dumps(value, ensure_ascii=False)
            line = f'      "{key}": {escaped_value}'

            # Add comma if not the last item
            if j < len(conv) - 1:
                line += ','

            lines.append(line)

        # Close conversation object
        if i < len(conversations) - 1:
            lines.append('    },')
        else:
            lines.append('    }')

    lines.append('  ]')
    lines.append('}')

    return '\n'.join(lines)


def fit_to_character_limit(conversations: List[List[Tuple[str, str]]],
                           character_limit: int) -> List[List[Tuple[str, str]]]:
    """
    Ensure total JSON length doesn't exceed character limit.
    Uses random sampling if needed.
    """
    # First try sequential
    result = []

    for conv in conversations:
        test_result = result + [conv]
        test_json = serialize_to_json_with_duplicate_keys(test_result)

        if len(test_json) <= character_limit:
            result = test_result
        else:
            break

    # If we got all conversations and still under limit, return
    if len(result) == len(conversations):
        return result

    # Otherwise, try random sampling to get more variety
    if len(result) < len(conversations):
        conversations_copy = conversations.copy()
        random.shuffle(conversations_copy)
        result = []

        for conv in conversations_copy:
            test_result = result + [conv]
            test_json = serialize_to_json_with_duplicate_keys(test_result)

            if len(test_json) <= character_limit:
                result = test_result
            else:
                break

    return result


def generate_conversation_json(input_file: str, output_file: str,
                               split_minutes: int, character_limit: int,
                               filter_media: bool, filter_links: bool,
                               user_name: str, char_name: str,
                               min_messages_per_conversation: int = 2,
                               media_replacement: Optional[str] = None,
                               link_replacement: Optional[str] = None):
    """
    Main function to convert WhatsApp chat to JSON format.

    Args:
        input_file: Path to WhatsApp .txt file
        output_file: Path for output .json file
        split_minutes: Time gap (minutes) to split conversations
        character_limit: Maximum JSON character count
        filter_media: Whether to remove <Media omitted> messages entirely
        filter_links: Whether to remove messages containing links entirely
        user_name: Username to map to {{random_user_1}}
        char_name: Username to map to {{char}}
        min_messages_per_conversation: Minimum messages required per conversation block (default: 2)
        media_replacement: If set and filter_media=False, replace media with this text (e.g., "<sends an attachment>")
        link_replacement: If set and filter_links=False, replace links with this text (e.g., "<sends a link>")
    """
    print(f"📖 Reading WhatsApp chat from: {input_file}")
    messages = parse_whatsapp_chat(input_file)
    print(f"✅ Parsed {len(messages)} messages")

    print(f"🔀 Grouping by {split_minutes} minute gaps...")
    blocks = group_by_time_gap(messages, split_minutes, filter_media, filter_links,
                               media_replacement, link_replacement)
    print(f"✅ Created {len(blocks)} conversation blocks")

    print(
        f"🚫 Filtering blocks (min {min_messages_per_conversation} messages, 2+ speakers)...")
    blocks = filter_single_speaker_blocks(
        blocks, min_messages_per_conversation)
    print(f"✅ {len(blocks)} blocks remaining after filtering")

    print("🔄 Converting to JSON format...")
    conversations = convert_to_json_format(blocks, user_name, char_name)
    print(f"✅ Generated {len(conversations)} conversation segments")

    print(f"📏 Fitting to {character_limit} character limit...")
    conversations = fit_to_character_limit(conversations, character_limit)
    print(f"✅ Final output: {len(conversations)} conversation segments")

    # Create final JSON string with duplicate keys support
    json_str = serialize_to_json_with_duplicate_keys(conversations)

    print(f"💾 Writing to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json_str)

    print(f"✅ Done! Final JSON size: {len(json_str)} characters")
    print(f"📊 Total conversation blocks: {len(conversations)}")


# Example usage
if __name__ == "__main__":
    generate_conversation_json(
        input_file="chat.txt", # Path to your WhatsApp chat export
        output_file="example_conversation.json", # Desired output path
        split_minutes=15, # Split conversations if gap > 15 minutes
        character_limit=20000, # Max characters in output JSON
        filter_media=True,  # True to remove media messages entirely, False to replace
        filter_links=True,  # True to remove link messages entirely, False to replace
        user_name="Razanius12", # Your WhatsApp username
        char_name="My Partner", # Chat partner's username
        min_messages_per_conversation=4,  # Minimum messages per conversation block
        media_replacement="<sends an attachment>",  # Replace media with this 'None' to keep original
        link_replacement="<sends a link>"  # Replace links with this 'None' to keep original
    )

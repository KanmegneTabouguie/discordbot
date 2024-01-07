import discord
import os
import replit
import requests
from discord.ext import commands

api_url = "https://groupietrackers.herokuapp.com/api/artists"

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def get_last_command(self):
        return self.head.data if self.head else None

    def get_all_commands(self):
        all_commands = [node.data for node in self.iterate_nodes()]
        return "\n".join(all_commands) if all_commands else None

    def clear_history(self):
        self.head = None

    def to_list(self):
        return [node.data for node in self.iterate_nodes()]

    @classmethod
    def from_list(cls, command_list):
        linked_list = cls()
        for command in command_list:
            linked_list.append(command)
        return linked_list

    def iterate_nodes(self):
        current_node = self.head
        while current_node:
            yield current_node
            current_node = current_node.next

class SimpleQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        return self.queue.pop(0) if self.queue else None

class BinaryTreeNode:
    def __init__(self, question, left=None, right=None, end_message=None):
        self.question = question
        self.left = left
        self.right = right
        self.end_message = end_message

class CommandHistoryManager:
    def __init__(self):
        self.command_history = {}  # Hashtable to store command history
        self.load_command_history()
        self.history_queue = SimpleQueue()
        self.history_locked = False
        self.questionnaire_completed = False

        # Binary tree for the questionnaire
        self.questionnaire_tree = BinaryTreeNode(
            "Is programming your favorite hobby?",
            left=BinaryTreeNode(
                "Do you enjoy coding?",
                left=BinaryTreeNode("Have you ever participated in a programming competition?"),
                right=BinaryTreeNode("Do you prefer web development over other types?")
            ),
            right=BinaryTreeNode(
                "Have you ever contributed to open-source projects?",
                left=BinaryTreeNode("Do you have a favorite programming language?"),
                right=BinaryTreeNode(
                    "Do you use version control systems like Git?",
                    left=BinaryTreeNode("End of questionnaire",
                                        end_message="You've completed the programming questionnaire!"),
                    right=None
                )
            )
        )

        # Dictionary to store information about different topics
        self.topic_information = {
            "python": "Python is a high-level, interpreted programming language...",
            "javascript": "JavaScript is a scripting language that enables you to create dynamically updating content...",
            # Add more topics and information as needed
        }

    async def initiate_questionnaire(self, channel, user_id):
        await self.ask_question(channel, self.questionnaire_tree, user_id)

    async def ask_question(self, channel, node, user_id, progress=0):
        if self.questionnaire_completed:
            return

        print(f"Asking question: {node.question}")
        await channel.send(node.question)

        response = await client.wait_for(
            'message',
            check=lambda m: m.channel == channel and m.author != client.user
        )

        print(f"Received response: {response.content}")
        user_history = self.get_user_history(user_id)
        print(f"User History: {user_history.to_list()}")

        if response.content.lower() in ['yes', 'no']:
            await self.add_command_to_history(user_history, response.content)
            self.command_history[user_id] = user_history

            progress += 1

            if progress < 8:
                if node.left:
                    await self.ask_question(channel, node.left, user_id, progress)

                if node.right:
                    await self.ask_question(channel, node.right, user_id, progress)
            else:
                print("Questionnaire completed!")
                self.questionnaire_completed = True
                if node.end_message:
                    await channel.send(node.end_message)
                else:
                    await channel.send(
                        "Thank you for completing the questionnaire! End of the questionnaire."
                    )
        else:
            print("Invalid response. Asking the same question again.")
            await channel.send("Invalid response. Please answer with 'yes' or 'no'.")

    def reset_conversation(self, user_id):
        if user_id in self.command_history:
            del self.command_history[user_id]

    def is_subject_covered(self, subject):
        return self._is_subject_covered_in_tree(subject, self.questionnaire_tree) or subject.lower() in self.topic_information

    def _is_subject_covered_in_tree(self, subject, node):
        if not node:
            return False

        if node.question.lower() == subject.lower():
            return True

        return (self._is_subject_covered_in_tree(subject, node.left)
                or self._is_subject_covered_in_tree(subject, node.right))

    def load_command_history(self):
        serialized_data = replit.db.get("command_history")
        if serialized_data:
            self.command_history = {
                user_id: LinkedList.from_list(command_list)
                for user_id, command_list in serialized_data.items()
            }
        else:
            self.command_history = {}

    def save_command_history(self):
        serialized_data = {
            user_id: user_history.to_list()
            for user_id, user_history in self.command_history.items()
        }
        replit.db["command_history"] = serialized_data

    def get_user_history(self, user_id):
        if user_id not in self.command_history:
            self.command_history[user_id] = LinkedList()
        return self.command_history[user_id]

    def clear_user_history(self, user_id):
        if user_id in self.command_history:
            self.command_history[user_id].clear_history()
            self.save_command_history()

    def is_history_locked(self):
        return self.history_locked

    def lock_history(self):
        self.history_locked = True

    def unlock_history(self):
        self.history_locked = False

    def enqueue_user(self, user_id):
        self.history_queue.enqueue(user_id)

    def dequeue_user(self):
        return self.history_queue.dequeue()

    async def add_command_to_history(self, user_history, command):
        print(f"Adding command to history for user {user_history}")
        user_history.append(command)
        print(f"Command added: {command}")

intents = discord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents)
command_history_manager = CommandHistoryManager()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    command_history_manager.load_command_history()

@client.event
async def on_member_join(member):
    print(f"User {member.name} joined the server.")

    welcome_channel_id = 1167398950945427539  # Replace with your welcome channel ID
    welcome_channel = client.get_channel(welcome_channel_id)

    if welcome_channel:
        await welcome_channel.send(f'Welcome {member.name}! Enjoy your time here.')

    user_id = str(member.id)

    # Wait for the initiate_questionnaire coroutine to complete before continuing
    await command_history_manager.initiate_questionnaire(welcome_channel,
                                                         user_id)

    print(f"Initialized data for user {user_id}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)
    user_history = command_history_manager.get_user_history(user_id)

    if command_history_manager.is_history_locked():
        await message.channel.send(
            "Command history is currently being processed. Please wait for your turn."
        )
        return

    command_history_manager.enqueue_user(user_id)

    while True:
        current_user = command_history_manager.dequeue_user()
        if current_user == user_id:
            break
        else:
            command_history_manager.enqueue_user(current_user)

    command_history_manager.lock_history()

    await command_history_manager.add_command_to_history(user_history, message.content)

    command_history_manager.save_command_history()
    command_history_manager.dequeue_user()

    command_history_manager.unlock_history()

    if message.guild:
        if message.content.lower() == '$lastcommand':
            await handle_last_command(message, user_history)
        elif message.content.lower() == '$allcommands':
            await handle_all_commands(message, user_history)
        elif message.content.lower() == '$hello':
            await handle_hello_command(message)
        elif message.content.lower() == '$clearhistory':
            await handle_clear_history(message, user_history)
        elif message.content.lower() == '$help':
            await handle_help_command(message)
        elif message.content.lower() == '$reset':
            await command_history_manager.handle_reset(message)
        elif message.content.lower().startswith('$speak about'):
            await handle_speak_about(message)
        elif message.content.lower() == '$artistinfos':
            await handle_artist_infos(message)

async def handle_last_command(message, user_history):
    last_command = user_history.get_last_command()
    if last_command:
        await message.channel.send(f'Last Command: {last_command}')
    else:
        await message.channel.send('No command history found.')

async def handle_all_commands(message, user_history):
    all_commands = user_history.get_all_commands()
    if all_commands:
        # Split the command history into chunks of 1900 characters to leave room for the message header
        chunks = [
            all_commands[i:i + 1900] for i in range(0, len(all_commands), 1900)
        ]

        for i, chunk in enumerate(chunks, start=1):
            await message.channel.send(f'All Commands - Part {i}:\n{chunk}')
    else:
        await message.channel.send('No command history found.')

async def handle_hello_command(message):
    await message.channel.send('Hello!')

async def handle_clear_history(message, user_history):
    user_id = str(message.author.id)
    command_history_manager.enqueue_user(user_id)

    while True:
        current_user = command_history_manager.dequeue_user()
        if current_user == user_id:
            break
        else:
            command_history_manager.enqueue_user(current_user)

    command_history_manager.clear_user_history(user_id)
    command_history_manager.save_command_history()
    command_history_manager.dequeue_user()

    await message.channel.send('Command history cleared.')

async def handle_help_command(message):
    # Extract the user ID from the message object
    user_id = str(message.author.id)

    # Send a welcome message to the user
    await message.channel.send("Welcome to the questionnaire! Let's get started.")

    # Initiate the questionnaire for the specific user
    await command_history_manager.initiate_questionnaire(message.channel,
                                                       user_id)

async def handle_speak_about(message):
    subject = message.content.lower().replace('$speak about', '').strip()
    if command_history_manager.is_subject_covered(subject):
        await message.channel.send(f"Yes, I can speak about {subject}.")
        # Check if information is available for the topic
        if subject in command_history_manager.topic_information:
            await message.channel.send(command_history_manager.topic_information[subject])
    else:
        await message.channel.send(f"Sorry, I don't have information about {subject}.")

async def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching content from {url}: {e}"

async def handle_artist_infos(message):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        artists_data = response.json()

        if artists_data:
            artist_infos = []
            for artist_data in artists_data:
                artist_name = artist_data['name']
                artist_id = artist_data['id']
                artist_image_url = artist_data.get('image', f"https://groupietrackers.herokuapp.com/api/images/{artist_name.lower().replace(' ', '_')}.jpeg")
                artist_members = artist_data.get('members', [])
                creation_date = artist_data.get('creationDate', 'N/A')
                first_album = artist_data.get('firstAlbum', 'N/A')
                locations_url = artist_data.get('locations', 'N/A')
                concert_dates_url = artist_data.get('concertDates', 'N/A')
                relations_url = artist_data.get('relations', 'N/A')

                locations_content = await fetch_url_content(locations_url)
                concert_dates_content = await fetch_url_content(concert_dates_url)
                relations_content = await fetch_url_content(relations_url)

                # Display artist information
                artist_message = await message.channel.send(f"Artist: {artist_name}\n"
                                                            f"Image: {artist_image_url}\n"
                                                            f"Members: {', '.join(artist_members)}\n"
                                                            f"Creation Date: {creation_date}\n"
                                                            f"First Album: {first_album}\n"
                                                            f"Locations:\n{locations_content}\n"
                                                            f"Concert Dates:\n{concert_dates_content}\n"
                                                            f"Relations:\n{relations_content}")

                artist_infos.append((artist_id, artist_name, artist_image_url, artist_members, creation_date, first_album, locations_content, concert_dates_content, relations_content))

            def reaction_check(reaction, user):
                return user == message.author and str(reaction.emoji) == "ℹ️"

            # Wait for the user to react with the information emoji
            reaction, _ = await client.wait_for('reaction_add', check=reaction_check, timeout=30)

            if reaction.emoji == "ℹ️":
                # Prompt the user to select an artist
                await message.channel.send("Please select an artist by typing its ID:")
                
                try:
                    artist_choice = await client.wait_for(
                        'message',
                        check=lambda m: m.channel == message.channel and m.author == message.author,
                        timeout=30.0
                    )

                    selected_artist_id = int(artist_choice.content)

                    # Find the selected artist in the artist_infos list
                    selected_artist = next((artist for artist in artist_infos if artist[0] == selected_artist_id), None)

                    if selected_artist:
                        artist_id, artist_name, artist_image_url, artist_members, creation_date, first_album, locations_content, concert_dates_content, relations_content = selected_artist
                        detailed_artist_info = fetch_artist_by_id(artist_id)

                        if detailed_artist_info:
                            # Display detailed artist information
                            await message.channel.send(f"Detailed Artist Information for {artist_name}:\n{detailed_artist_info}\nImage: {artist_image_url}\n"
                                                       f"Members: {', '.join(artist_members)}\n"
                                                       f"Creation Date: {creation_date}\n"
                                                       f"First Album: {first_album}\n"
                                                       f"Locations:\n{locations_content}\n"
                                                       f"Concert Dates:\n{concert_dates_content}\n"
                                                       f"Relations:\n{relations_content}")
                        else:
                            await message.channel.send(f"Failed to fetch detailed information for {artist_name}.")
                    else:
                        await message.channel.send("Invalid artist ID. Please try again.")

                except ValueError:
                    await message.channel.send("Invalid input. Please enter a valid artist ID.")

        else:
            await message.channel.send("No artist information available.")

    except Exception as e:
        await message.channel.send(f"Error fetching artist information: {e}")


def fetch_artist_by_id(artist_id):
    detailed_api_url = f"https://groupietrackers.herokuapp.com/api/artists/{artist_id}"

    try:
        response = requests.get(detailed_api_url)
        response.raise_for_status()
        detailed_artist_info = response.json()

        return detailed_artist_info

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None

    except Exception as e:
        print(f"Error fetching artist information: {e}")
        return None

@client.event
async def on_disconnect():
    print("Bot disconnected. Saving data.")
    command_history_manager.save_command_history()

client.run(os.getenv('TOKEN'))

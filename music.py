import discord
import yt_dlp
import asyncio
import random


class MusicPlayer:

    def __init__(self):
        self.voice_clients = {}
        self.playlist = []

    def add_to_playlist(self, url):
        self.playlist.append(url)

    async def join_and_play(self,
                            interaction: discord.Interaction = None,
                            url: str = None,
                            force_voice_channel: bool = False):
        if not force_voice_channel and interaction and (not interaction.user or not interaction.user.voice):
            if interaction:
                await interaction.followup.send(
                    "You must be in a voice channel to use this command!")
            return

        # Check if ffmpeg is installed
        import shutil
        if not shutil.which('ffmpeg'):
            if interaction:
                await interaction.followup.send(
                    "Error: ffmpeg is not installed. Please contact the bot administrator.")
            return

        try:
            # Determine the guild ID based on whether an interaction is provided
            guild_id = interaction.guild.id if interaction else list(self.voice_clients.keys())[0] if self.voice_clients else None
            if guild_id is None:
                if interaction:
                    await interaction.followup.send("Bot is not connected to any voice channel.")
                return

            # Get or create a voice client
            voice_client = self.voice_clients.get(guild_id)
            if not voice_client:
                if interaction:
                    channel = interaction.user.voice.channel
                else:
                    # Attempt to get a channel from the first guild in the client list.  This is a fallback and may fail.
                    channel = list(self.voice_clients.values())[0].channel
                voice_client = await channel.connect()
                self.voice_clients[guild_id] = voice_client

            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if url is None and self.playlist:
                    # Play random song from playlist
                    url = random.choice(self.playlist)

                if url:
                    try:
                        # Extract video info
                        info = ydl.extract_info(url, download=False)
                        if 'entries' in info:
                            # Handle playlist URL - get all valid entries first
                            valid_entries = [entry for entry in info['entries'] if entry is not None]
                            if not valid_entries:
                                raise Exception("No valid videos found in playlist")
                            # Select random video from valid entries
                            video = random.choice(valid_entries)
                            url = f"https://www.youtube.com/watch?v={video['id']}"
                            # Get specific video info
                            info = ydl.extract_info(url, download=False, force_generic_extractor=False)

                        # Get audio stream URL
                        audio_url = info['url']

                        # Create audio source and play with delay
                        await asyncio.sleep(1)  # Wait before playing
                        source = await discord.FFmpegOpusAudio.from_probe(
                            audio_url,
                            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
                        voice_client.play(source)

                        # Send confirmation message if interaction is available
                        if interaction:
                            await interaction.followup.send(
                                f"🎵 Now playing: {info.get('title', 'Unknown')}")

                        # Wait until song finishes
                        while voice_client.is_playing():
                            await asyncio.sleep(1)

                    except Exception as e:
                        if interaction:
                            await interaction.followup.send(
                                f"Error playing song: {str(e)}")
                else:
                    if interaction:
                        await interaction.followup.send(
                            "No URL provided and playlist is empty!")

                # Disconnect after playing if not force_voice_channel
                if not force_voice_channel:
                    await voice_client.disconnect()
                    del self.voice_clients[guild_id]

        except Exception as e:
            if interaction:
                await interaction.followup.send(f"Error: {str(e)}")
            if guild_id in self.voice_clients:
                await self.voice_clients[guild_id].disconnect()
                del self.voice_clients[guild_id]
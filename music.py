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
                            interaction: discord.Interaction,
                            url: str = None):
        try:
            if not interaction.user or not interaction.user.voice:
                await interaction.followup.send(
                    "You must be in a voice channel to use this command!")
                return

            # Check if ffmpeg is installed
            import shutil
            if not shutil.which('ffmpeg'):
                await interaction.followup.send(
                    "Error: ffmpeg is not installed. Please contact the bot administrator.")
                return

        try:
            channel = interaction.user.voice.channel
            voice_client = await channel.connect()
            self.voice_clients[interaction.guild.id] = voice_client

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
                            # Handle playlist URL
                            video = random.choice(info['entries'])
                            url = f"https://www.youtube.com/watch?v={video['id']}"
                            info = ydl.extract_info(url, download=False)

                        # Get audio stream URL
                        audio_url = info['url']

                        # Create audio source and play
                        source = await discord.FFmpegOpusAudio.from_probe(
                            audio_url)
                        voice_client.play(source)

                        # Send confirmation message
                        await interaction.followup.send(
                            f"🎵 Now playing: {info.get('title', 'Unknown')}")

                        # Wait until song finishes
                        while voice_client.is_playing():
                            await asyncio.sleep(1)

                    except Exception as e:
                        await interaction.followup.send(
                            f"Error playing song: {str(e)}")
                else:
                    await interaction.followup.send(
                        "No URL provided and playlist is empty!")

            # Disconnect after playing
            await voice_client.disconnect()
            del self.voice_clients[interaction.guild.id]

        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
            if interaction.guild.id in self.voice_clients:
                await voice_client.disconnect()
                del self.voice_clients[interaction.guild.id]

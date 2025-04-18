
import discord
import yt_dlp
import asyncio
import json
from pathlib import Path

class MusicPlayer:
    def __init__(self):
        self.voice_clients = {}
        self.config_file = "music_config.json"
        self.playlist = []
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.playlist = config.get('playlist', [])
        except FileNotFoundError:
            self.playlist = []

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'playlist': self.playlist}, f, indent=4)

    async def join_and_play(self, ctx, url=None):
        if not ctx.author.voice:
            await ctx.send("You must be in a voice channel!")
            return

        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        self.voice_clients[ctx.guild.id] = voice_client

        if url is None and self.playlist:
            import random
            url = random.choice(self.playlist)

        if url:
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2)
                voice_client.play(source)

                while voice_client.is_playing():
                    await asyncio.sleep(1)
                
                await voice_client.disconnect()
                del self.voice_clients[ctx.guild.id]

    def add_to_playlist(self, url):
        if url not in self.playlist:
            self.playlist.append(url)
            self.save_config()


import discord
import yt_dlp
import asyncio
import random

class MusicPlayer:
    def __init__(self):
        self.voice_clients = {}
        
    async def join_and_play(self, ctx, playlist_url):
        if not ctx.author or not ctx.author.voice:
            await ctx.send("Unable to join voice channel!")
            return

        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        self.voice_clients[ctx.guild.id] = voice_client

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'extract_flat': True,
                'playlistrandom': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract playlist info
                info = ydl.extract_info(playlist_url, download=False)
                if 'entries' in info:
                    # Randomly select a video from playlist
                    video = random.choice(info['entries'])
                    video_url = f"https://www.youtube.com/watch?v={video['id']}"
                    
                    # Get the audio stream URL
                    video_info = ydl.extract_info(video_url, download=False)
                    url = video_info['url']
                    
                    # Play the audio
                    source = await discord.FFmpegOpusAudio.from_probe(url)
                    voice_client.play(source)

                    # Wait until the song finishes
                    while voice_client.is_playing():
                        await asyncio.sleep(1)

            # Disconnect after playing
            await voice_client.disconnect()
            del self.voice_clients[ctx.guild.id]
            
        except Exception as e:
            print(f"Error playing music: {e}")
            if ctx.guild.id in self.voice_clients:
                await voice_client.disconnect()
                del self.voice_clients[ctx.guild.id]
import discord
import yt_dlp
import asyncio
import random

class MusicPlayer:
    def __init__(self):
        self.voice_clients = {}
        
    async def join_and_play(self, ctx, playlist_url=None):
        if not ctx.author or not ctx.author.voice:
            await ctx.send("Unable to join voice channel!")
            return

        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        self.voice_clients[ctx.guild.id] = voice_client

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'extract_flat': True,
                'playlistrandom': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if playlist_url:
                    # Extract playlist info
                    info = ydl.extract_info(playlist_url, download=False)
                    if 'entries' in info:
                        # Randomly select a video from playlist
                        video = random.choice(info['entries'])
                        video_url = f"https://www.youtube.com/watch?v={video['id']}"
                else:
                    video_url = playlist_url

                # Get the audio stream URL
                video_info = ydl.extract_info(video_url, download=False)
                url = video_info['url']
                
                # Play the audio
                source = await discord.FFmpegOpusAudio.from_probe(url)
                voice_client.play(source)

                # Wait until the song finishes
                while voice_client.is_playing():
                    await asyncio.sleep(1)

            # Disconnect after playing
            await voice_client.disconnect()
            del self.voice_clients[ctx.guild.id]
            
        except Exception as e:
            print(f"Error playing music: {e}")
            if ctx.guild.id in self.voice_clients:
                await voice_client.disconnect()
                del self.voice_clients[ctx.guild.id]

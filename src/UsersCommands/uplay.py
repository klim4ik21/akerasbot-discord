import disnake
from disnake.ext import commands, tasks
import yt_dlp
import json
import random
from logs.log import log_action, error_action

rand_enjo_music = ['🎶 Lets!', '🎙️ Vibe!', '🎸 Rock?']


class nMusicPlay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = None
        self.music_queue = []
        self.last_song_url = None
        self.control_message = None
        self.check_voice_channel.start()
        self.is_paused = False

    async def song_end_callback(self):
        try:
            if self.current_message:
                embed = self.current_message.embeds[0]
                embed.title = embed.title.replace("<a:playing:1191024834726088744>", "")
                await self.current_message.edit(embed=embed, view=None)
        except Exception as e:
            error_action(e)
            print(f"An error occurred in song_end_callback: {e}")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            if after.channel:
                self.voice_channel = after.channel
            else:
                self.voice_channel = None

    class MusicControls(disnake.ui.View):
        def __init__(self, music_cog, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.music_cog = music_cog

            self.pause_button = disnake.ui.Button(
                label="Pause", 
                emoji="<:pause100:1191004291671007332>", 
                style=disnake.ButtonStyle.blurple, 
                custom_id="pause_button"
            )
            self.play_button = disnake.ui.Button(
                label="Play", 
                emoji="<:play100:1191003901353279488>", 
                style=disnake.ButtonStyle.green, 
                custom_id="play_button",
                disabled=True
            )

            self.skip_button = disnake.ui.Button(
            label="Skip", 
            emoji="<:forward100:1191004245416230912>", 
            style=disnake.ButtonStyle.red, 
            custom_id="skip_button"
        )

            self.add_item(self.pause_button)
            self.add_item(self.play_button)
            self.add_item(self.skip_button)

            self.pause_button.callback = self.pause_button_callback
            self.play_button.callback = self.play_button_callback
            self.skip_button.callback = self.skip_button_callback

        async def pause_button_callback(self, interaction):
            await interaction.response.defer()
            await self.music_cog.pause(interaction, send_message=False)
            self.pause_button.disabled = True
            self.play_button.disabled = False
            await interaction.message.edit(view=self)

        async def play_button_callback(self, interaction):
            await interaction.response.defer()
            await self.music_cog.unpause(interaction, send_message=False)
            self.pause_button.disabled = False
            self.play_button.disabled = True
            await interaction.message.edit(view=self)

        async def skip_button_callback(self, interaction):
            await interaction.response.defer()
            await self.music_cog.skip(interaction, send_message=False)


    async def connect_to_voice(self, ctx):
        if not self.voice_channel:
            if ctx.author.voice:
                self.voice_channel = ctx.author.voice.channel
            else:
                await ctx.send("You are not in a voice channel. Please join a voice channel first.")
                return
        
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            if voice_client.guild == ctx.guild:  # Corrected line
                print("Already connected to the voice channel.")
                return
        
        await self.voice_channel.connect()

    async def play_song(self, ctx, query=None):
        try:
            ydl_opts = {'format': 'bestaudio', 'noplaylist': 'False'}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if query:
                    if query.startswith('http://') or query.startswith('https://'):
                        info = ydl.extract_info(query, download=False)
                        if 'entries' in info:  # It's a playlist
                            playlist_title = info.get('title', 'Unknown Playlist')
                            await ctx.send(f"Adding playlist: {playlist_title}")
                            for entry in info['entries']:
                                self.music_queue.append(entry['webpage_url'])
                            await ctx.send(f"Added {len(info['entries'])} songs to the queue from the playlist.")
                            return
                        else:  # It's a single video
                            url = info['url']
                    else:
                        # Perform a YouTube search
                        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                        url = info['url']
                else:
                    if self.last_song_url:
                        info = ydl.extract_info(self.last_song_url, download=False)
                        url = info['url']
                    else:
                        await ctx.send("No song to play.")
                        return

                url = info['url']
                video_info = info
                thumbnail_url = video_info.get('thumbnails', [{}])[0].get('url')
                video_url = video_info.get('webpage_url', 'No URL available')
                title = video_info['title']
                duration = video_info.get('duration', 0)

                if "Kai Angel" in title or "9mice" in title:
                    klimid = ctx.guild.get_member(int("468445928878112793"))
                    if klimid is not None and klimid.voice is not None and klimid.voice.channel == ctx.author.voice.channel:
                        await ctx.send("Я не буду это включать, у меня будут болеть уши!")
                        return

            await self.connect_to_voice(ctx)

            voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice_client:
                if voice_client.is_playing():
                    voice_client.stop()

                source = disnake.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn')
                voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.song_end_callback(ctx, message)))
                self.last_song_url = url
                minutes, seconds = divmod(duration, 60)
                duration_formatted = f"{minutes} минут {seconds} секунд"
                user_avatar_url = str(ctx.author.avatar.url)
                custom_emoji = "<a:playing:1191024834726088744>"
                embed = disnake.Embed(
                    title=f"{custom_emoji} {title}",
                    description=f"**Duration song:** {duration_formatted}\n[Youtube link]({video_url})",
                    color=0xfac6d9
                )
                embed.set_author(name=ctx.author.display_name, icon_url=user_avatar_url)
                embed.set_thumbnail(url=thumbnail_url)
                embed.set_footer(text=random.choice(rand_enjo_music))
                music_cog = self.bot.get_cog("nMusicPlay")
                view = self.MusicControls(music_cog)

                
                message = await ctx.followup.send(embed=embed, view=view)
                
            else:
                await ctx.send("Failed to connect to the voice channel.")
        except Exception as e:
            error_action(e)
            print(f"An error occurred in play_song: {e}")
            await ctx.send(f"An error occurred: {e}")

    async def disconnect_from_voice(self, guild):
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
    
    @tasks.loop(minutes=1)
    async def check_voice_channel(self):
        if self.voice_channel:
            members_in_channel = [member for member in self.voice_channel.members if not member.bot]
            if not members_in_channel:
                self.music_queue.clear()
                self.disconnect_from_voice(self.voice_channel.guild)
                return

            voice_client = disnake.utils.get(self.bot.voice_clients, guild=self.voice_channel.guild)
            if voice_client and not voice_client.is_playing() and not voice_client.is_paused():
                await self.play_next_song(self.voice_channel.guild)
    
    async def play_next_song(self, interaction):
        if self.music_queue:
            next_song = self.music_queue.pop(0)
            await self.play_song(interaction, next_song)
        else:
            await self.disconnect_from_voice(self.voice_channel)

    @commands.slash_command(name="nplay", description="Play a song by searching for its title or resume the last song.")
    async def play(self, inter, songname: str = None):
        await inter.response.defer()

        # Подключение к голосовому каналу, если бот ещё не подключен
        if not self.voice_channel or not self.bot.voice_clients:
            await self.connect_to_voice(inter)

        # Добавление песни в очередь, если указано имя песни
        if songname:
            self.music_queue.append(songname)
            await inter.followup.send(f"Added `{songname}` to the queue.")

        # Получение клиента голосового канала
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=inter.guild)

        # Воспроизведение следующей песни из очереди, если в данный момент ничего не воспроизводится
        if not voice_client.is_playing() and not voice_client.is_paused():
            await self.play_next_song(inter)


    @commands.slash_command(name="splay", description="Play a song by searching for its title and skip the current song.")
    async def skip_play(self, inter, songname: str):
        await inter.response.defer()

        if not self.voice_channel or not self.bot.voice_clients:
            await self.connect_to_voice(inter)

        self.music_queue.insert(0, songname)

        if self.bot.voice_clients[0].is_playing() or self.bot.voice_clients[0].is_paused():
            await self.play_next_song(inter)
        else:
            await inter.followup.send(f"Added `{songname}` to the queue.")

    @commands.slash_command(name="bassboost", description="Apply hard bass boost effect to the currently playing song.")
    async def bassboost(self, inter, equal: int):
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=inter.guild)
        eq1 = 150
        eq3 = 10
        if int(equal) == 1:
            eq1 = 150
            eq3 = 10
        elif int(equal) == 2:
            eq1=199
            eq3=21
        elif int(equal) == 3:
            eq1 = 300
            eq3 = 28
        else:
            eq1 = 150
            eq3= 10

        
        if voice_client and voice_client.is_playing():
            url = self.last_song_url if self.last_song_url else self.music_queue[0]
            bass_boost_filter = f'compand=0|0:1|1:-90/-60/-30/-15/-15/-10/0/0:{eq1}:0:0:0, equalizer=f=50:width_type=h:width=100:g={eq3}'
            source = disnake.FFmpegPCMAudio(url, options=f'-af "{bass_boost_filter}"')
            
            # Stop the current playback and play the bass-boosted version from the saved position
            voice_client.stop()
            voice_client.play(source)
            
            await inter.response.send_message("Applied hard bass boost effect.")
        else:
            await inter.response.send_message("No song is currently playing.")


    @commands.slash_command(name="nskip", description="Skip the current song in the queue.")
    async def skip(self, interaction, send_message=True):
        await interaction.response.defer()

        voice_client = disnake.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            if send_message == False:
                if self.music_queue:  # Добавить проверку, есть ли треки в очереди
                    await self.play_next_song(interaction)
                    await interaction.followup.send("Skipped the current song.")
                else:
                    await interaction.followup.send("Skipped the song, but the queue is empty.")
        else:
            await interaction.followup.send("No song is currently playing.")


    @commands.slash_command(name="cqueue", description="Clear the music queue.")
    async def clear_queue(self, ctx):
            self.music_queue.clear()
            message = await ctx.send("Cleared the music queue.")
            print(message)

    @commands.slash_command(name="nqueue", description="Display the current music queue.")
    async def queue(self, inter):
            await inter.response.defer()
            await self.send_queue_embed(inter)

    async def send_queue_embed(self, inter):
            if not self.music_queue:
                await inter.followup.send("The music queue is empty.")
                return

            queue_info = "\n".join([f"{index + 1}. {track}" for index, track in enumerate(self.music_queue)])

            embed = disnake.Embed(
                title="Music Queue",
                description=queue_info,
                color=0xfac6d9
            )

            await inter.followup.send(embed=embed)

    @commands.slash_command(name="unpause", description="Resume the paused song.")
    async def unpause(self, interaction, send_message=True):
            voice_client = disnake.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if voice_client and voice_client.is_paused():
                voice_client.resume()
                if send_message:
                    await interaction.followup.send("Resumed the paused song.")
                else:
                    embed = interaction.message.embeds[0]
                    embed.title = f"<a:playing:1191024834726088744> {embed.title}"
                    await interaction.message.edit(embed=embed)
            else:
                if send_message:
                    await interaction.followup.send("No song is currently paused.")

    @commands.slash_command(name="npause", description="Pause the current song.")
    async def pause(self, interaction, send_message=True):
            voice_client = disnake.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if voice_client and voice_client.is_playing():
                voice_client.pause()
                if send_message:
                    await interaction.followup.send("Paused the current song.")
                else:
                    embed = interaction.message.embeds[0]
                    embed.title = embed.title.replace("<a:playing:1191024834726088744>", "")
                    await interaction.message.edit(embed=embed)
            else:
                if send_message:
                    await interaction.followup.send("No song is currently playing.")


    @commands.slash_command(name="nstop", description="⏸Song Stopped")
    async def stop(self, ctx):
        await ctx.send("Processing your request...")

        voice_client = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Stopped the current song.")
            await self.play_next_song(ctx)
        else:
            await ctx.send("No song is currently playing.")

    def save_queue_to_json(self):
        with open("music_queue.json", "w") as json_file:
            json.dump(self.music_queue, json_file)

    def load_queue_from_json(self):
        try:
            with open("music_queue.json", "r") as json_file:
                self.music_queue = json.load(json_file)
        except FileNotFoundError:
            error_action("MUSIC QUEUE - FIleNotFoundError")
            # If the file doesn't exist, initialize an empty queue
            self.music_queue = []

    def cog_unload(self):
        self.save_queue_to_json()

def setup(bot):
    nmusic_cog = nMusicPlay(bot)
    nmusic_cog.load_queue_from_json()
    bot.add_cog(nmusic_cog)
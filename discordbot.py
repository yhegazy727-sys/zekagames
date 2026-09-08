import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import random
import asyncio
from typing import List, Dict, Optional

# ================== Bot Setup ==================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# ================== Game Data ==================
ARABIC_WORDS = [
    "مدرسة", "كتاب", "قلم", "شجرة", "سيارة", "بيت", "مكتب", "طاولة", 
    "كرسي", "نافذة", "باب", "حديقة", "زهرة", "شمس", "قمر", "نجم",
    "ماء", "هواء", "نار", "تراب", "جبل", "بحر", "نهر", "صحراء",
    "مدينة", "قرية", "طريق", "جسر", "ميدان", "حديقة", "متحف", "مسجد",
    "اليابان", "أمريكا", "فرنسا", "مصر", "سوريا", "العراق", "الأردن", "لبنان"
]

# ================== Leaderboard System ==================
user_scores = {}

def add_score(user_id: int, points: int = 1):
    user_scores[user_id] = user_scores.get(user_id, 0) + points
    return user_scores[user_id]

# ================== Main Menu View ==================
class MainMenuView(View):
    def __init__(self):
        super().__init__(timeout=180)
        
    @discord.ui.select(
        placeholder="اختر نوع اللعبة...",
        options=[
            discord.SelectOption(
                label="ألعاب فردية",
                description="ألعاب سريعة وتحديات فردية",
                emoji="⚡",
                value="single"
            ),
            discord.SelectOption(
                label="ألعاب جماعية",
                description="ألعاب حفلات وتحديات جماعية",
                emoji="👥",
                value="multi"
            )
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: Select):
        if select.values[0] == "single":
            view = SinglePlayerMenuView()
            embed = discord.Embed(
                title="⚡ ألعاب فردية",
                description="اختر اللعبة التي تريد أن تلعبها:",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            view = MultiPlayerMenuView()
            embed = discord.Embed(
                title="👥 ألعاب جماعية",
                description="اختر اللعبة التي تريد أن تلعبها:",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=view)

# ================== Single Player Menu ==================
class SinglePlayerMenuView(View):
    def __init__(self):
        super().__init__(timeout=180)
        
    @discord.ui.select(
        placeholder="اختر لعبة فردية...",
        options=[
            discord.SelectOption(
                label="لعبة الكلمة",
                description="اكتب الكلمة بسرعة!",
                emoji="⌨️",
                value="word"
            ),
            discord.SelectOption(
                label="لعبة التفكيك",
                description="فكك الكلمة حرف بحرف",
                emoji="🔤",
                value="disassemble"
            ),
            discord.SelectOption(
                label="لعبة الترتيب",
                description="رتب الحروف لتكوين الكلمة",
                emoji="🔀",
                value="unscramble"
            ),
            discord.SelectOption(
                label="لعبة التجميع",
                description="جمع الحروف لتكوين كلمة صحيحة",
                emoji="🧩",
                value="assemble"
            ),
            discord.SelectOption(
                label="العودة للقائمة الرئيسية",
                emoji="🔙",
                value="back"
            )
        ]
    )
    async def select_game(self, interaction: discord.Interaction, select: Select):
        if select.values[0] == "back":
            view = MainMenuView()
            embed = discord.Embed(
                title="هذه هي ألعاب هذا البوت",
                description="اختر الفئة المناسبة:",
                color=discord.Color.gold()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            return
            
        await interaction.response.defer()
        
        if select.values[0] == "word":
            await start_word_game(interaction)
        elif select.values[0] == "disassemble":
            await start_disassemble_game(interaction)
        elif select.values[0] == "unscramble":
            await start_unscramble_game(interaction)
        elif select.values[0] == "assemble":
            await start_assemble_game(interaction)

# ================== Single Player Games ==================
async def start_word_game(interaction: discord.Interaction):
    word = random.choice(ARABIC_WORDS)
    embed = discord.Embed(
        title="⌨️ لعبة الكلمة",
        description=f"**اكتب هذه الكلمة بسرعة:**\n\n**{word}**",
        color=discord.Color.blue()
    )
    embed.set_footer(text="لديك 15 ثانية!")
    await interaction.followup.send(embed=embed)
    
    def check(m):
        return m.channel == interaction.channel and m.content == word
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        score = add_score(msg.author.id)
        win_embed = discord.Embed(
            title="🎉 فائز!",
            description=f"{msg.author.mention} كتب الكلمة بشكل صحيح!\n**النقاط الكلية:** {score}",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=win_embed)
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ انتهى الوقت!",
            description=f"الكلمة الصحيحة كانت: **{word}**",
            color=discord.Color.red()
        )
        await interaction.channel.send(embed=timeout_embed)

async def start_disassemble_game(interaction: discord.Interaction):
    word = random.choice(ARABIC_WORDS)
    correct_answer = " ".join(list(word))
    
    embed = discord.Embed(
        title="🔤 لعبة التفكيك",
        description=f"**فكك هذه الكلمة حرف بحرف:**\n\n**{word}**\n\nمثال: اليابان → ا ل ي ا ب ا ن",
        color=discord.Color.purple()
    )
    embed.set_footer(text="لديك 20 ثانية!")
    await interaction.followup.send(embed=embed)
    
    def check(m):
        return m.channel == interaction.channel and m.content == correct_answer
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=20.0)
        score = add_score(msg.author.id)
        win_embed = discord.Embed(
            title="🎉 فائز!",
            description=f"{msg.author.mention} فكك الكلمة بشكل صحيح!\n**النقاط الكلية:** {score}",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=win_embed)
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ انتهى الوقت!",
            description=f"الإجابة الصحيحة كانت: **{correct_answer}**",
            color=discord.Color.red()
        )
        await interaction.channel.send(embed=timeout_embed)

async def start_unscramble_game(interaction: discord.Interaction):
    word = random.choice(ARABIC_WORDS)
    scrambled = ''.join(random.sample(word, len(word)))
    
    # Ensure it's actually scrambled
    attempts = 0
    while scrambled == word and attempts < 10:
        scrambled = ''.join(random.sample(word, len(word)))
        attempts += 1
    
    embed = discord.Embed(
        title="🔀 لعبة الترتيب",
        description=f"**رتب هذه الحروف لتكوين كلمة صحيحة:**\n\n**{scrambled}**",
        color=discord.Color.orange()
    )
    embed.set_footer(text="لديك 20 ثانية!")
    await interaction.followup.send(embed=embed)
    
    def check(m):
        return m.channel == interaction.channel and m.content == word
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=20.0)
        score = add_score(msg.author.id)
        win_embed = discord.Embed(
            title="🎉 فائز!",
            description=f"{msg.author.mention} رتب الكلمة بشكل صحيح!\n**النقاط الكلية:** {score}",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=win_embed)
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ انتهى الوقت!",
            description=f"الكلمة الصحيحة كانت: **{word}**",
            color=discord.Color.red()
        )
        await interaction.channel.send(embed=timeout_embed)

async def start_assemble_game(interaction: discord.Interaction):
    word = random.choice(ARABIC_WORDS)
    letters = list(word)
    random.shuffle(letters)
    scrambled = " ".join(letters)
    
    embed = discord.Embed(
        title="🧩 لعبة التجميع",
        description=f"**جمع هذه الحروف لتكوين كلمة صحيحة:**\n\n**{scrambled}**",
        color=discord.Color.magenta()
    )
    embed.set_footer(text="لديك 20 ثانية!")
    await interaction.followup.send(embed=embed)
    
    def check(m):
        return m.channel == interaction.channel and m.content == word
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=20.0)
        score = add_score(msg.author.id)
        win_embed = discord.Embed(
            title="🎉 فائز!",
            description=f"{msg.author.mention} جمع الكلمة بشكل صحيح!\n**النقاط الكلية:** {score}",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=win_embed)
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ انتهى الوقت!",
            description=f"الكلمة الصحيحة كانت: **{word}**",
            color=discord.Color.red()
        )
        await interaction.channel.send(embed=timeout_embed)

# ================== Multiplayer Menu ==================
class MultiPlayerMenuView(View):
    def __init__(self):
        super().__init__(timeout=180)
        
    @discord.ui.select(
        placeholder="اختر لعبة جماعية...",
        options=[
            discord.SelectOption(
                label="لعبة بيننا",
                description="لعبة القاتل والمحقق (3+ لاعبين)",
                emoji="🔪",
                value="among"
            ),
            discord.SelectOption(
                label="لعبة المافيا",
                description="لعبة المافيا الكلاسيكية",
                emoji="🕵️",
                value="mafia"
            ),
            discord.SelectOption(
                label="لعبة الروليت",
                description="عجلة الحظ - آخر لاعب يفوز",
                emoji="🎡",
                value="roulette"
            ),
            discord.SelectOption(
                label="العودة للقائمة الرئيسية",
                emoji="🔙",
                value="back"
            )
        ]
    )
    async def select_game(self, interaction: discord.Interaction, select: Select):
        if select.values[0] == "back":
            view = MainMenuView()
            embed = discord.Embed(
                title="هذه هي ألعاب هذا البوت",
                description="اختر الفئة المناسبة:",
                color=discord.Color.gold()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            return
            
        if select.values[0] == "among":
            await interaction.response.send_message("جاري تجهيز لعبة بيننا...", ephemeral=True)
            await start_among_us_game(interaction)
        elif select.values[0] == "mafia":
            await interaction.response.send_message("جاري تجهيز لعبة المافيا...", ephemeral=True)
            await start_mafia_game(interaction)
        elif select.values[0] == "roulette":
            await interaction.response.send_message("جاري تجهيز لعبة الروليت...", ephemeral=True)
            await start_roulette_game(interaction)

# ================== Among Us Game ==================
class AmongUsJoinView(View):
    def __init__(self, game_manager):
        super().__init__(timeout=60)
        self.game_manager = game_manager
        
    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.green, emoji="✅")
    async def join_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id in self.game_manager.players:
            await interaction.response.send_message("أنت مشترك بالفعل في اللعبة!", ephemeral=True)
        else:
            self.game_manager.players.append(interaction.user.id)
            await interaction.response.send_message("تم الانضمام بنجاح! 🎮", ephemeral=True)
            
            # Update the embed
            embed = discord.Embed(
                title="🔪 لعبة بيننا",
                description=f"**عدد اللاعبين:** {len(self.game_manager.players)}\n\nانتظر حتى يبدأ منظم اللعبة!",
                color=discord.Color.red()
            )
            await interaction.message.edit(embed=embed)
    
    @discord.ui.button(label="ابدأ اللعبة", style=discord.ButtonStyle.blurple, emoji="▶️")
    async def start_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.game_manager.starter_id:
            await interaction.response.send_message("فقط من بدأ اللعبة يمكنه تشغيلها!", ephemeral=True)
            return
            
        if len(self.game_manager.players) < 3:
            await interaction.response.send_message("يجب أن يكون هناك 3 لاعبين على الأقل!", ephemeral=True)
            return
        
        await interaction.response.send_message("جاري بدء اللعبة...", ephemeral=True)
        self.stop()
        await self.game_manager.start_game(interaction)

class AmongUsGameManager:
    def __init__(self, channel, starter_id):
        self.channel = channel
        self.starter_id = starter_id
        self.players: List[int] = []
        self.impostor = None
        self.detective = None
        self.alive_players = []
        self.dead_players = []
        self.lights_on = True
        
    async def start_game(self, interaction: discord.Interaction):
        self.alive_players = self.players.copy()
        
        # Assign roles
        self.impostor = random.choice(self.players)
        remaining = [p for p in self.players if p != self.impostor]
        self.detective = random.choice(remaining) if len(remaining) > 0 else None
        
        # Send role notifications
        for player_id in self.players:
            user = await bot.fetch_user(player_id)
            
            if player_id == self.impostor:
                embed = discord.Embed(
                    title="🔪 دورك: القاتل",
                    description="أنت القاتل! هدفك هو قتل جميع اللاعبين دون أن يتم اكتشافك.",
                    color=discord.Color.red()
                )
                view = ImpostorControlView(self)
                await self.channel.send(f"{user.mention}", embed=embed, view=view, delete_after=0.1)
                
            elif player_id == self.detective:
                embed = discord.Embed(
                    title="🕵️ دورك: المحقق",
                    description="أنت المحقق! حاول اكتشاف القاتل قبل أن يقتل الجميع.",
                    color=discord.Color.blue()
                )
                await self.channel.send(f"{user.mention}", embed=embed, delete_after=0.1)
                
            else:
                embed = discord.Embed(
                    title="👤 دورك: مواطن",
                    description="أنت مواطن عادي. حاول البقاء على قيد الحياة واكتشاف القاتل!",
                    color=discord.Color.green()
                )
                await self.channel.send(f"{user.mention}", embed=embed, delete_after=0.1)
        
        # Game started message
        game_embed = discord.Embed(
            title="🎮 بدأت اللعبة!",
            description=f"**عدد اللاعبين:** {len(self.players)}\n**القاتل:** ؟؟؟\n**المحقق:** ؟؟؟",
            color=discord.Color.gold()
        )
        await self.channel.send(embed=game_embed)
        
    def check_win_condition(self):
        alive_count = len(self.alive_players)
        if self.impostor not in self.alive_players:
            return "crew"  # Crew wins
        elif alive_count <= 2:
            return "impostor"  # Impostor wins
        return None
    
    async def kill_player(self, victim_id, interaction):
        if victim_id in self.alive_players:
            self.alive_players.remove(victim_id)
            self.dead_players.append(victim_id)
            
            victim = await bot.fetch_user(victim_id)
            kill_embed = discord.Embed(
                title="💀 تم العثور على جثة!",
                description=f"**{victim.mention}** تم قتله!",
                color=discord.Color.dark_red()
            )
            await self.channel.send(embed=kill_embed)
            
            # Check win condition
            winner = self.check_win_condition()
            if winner:
                await self.end_game(winner)
            else:
                await self.start_voting()
    
    async def start_voting(self):
        vote_embed = discord.Embed(
            title="🗳️ وقت التصويت!",
            description="ناقشوا من تعتقدون أنه القاتل واختاروا من تريدون طرده!",
            color=discord.Color.blue()
        )
        
        view = VotingView(self)
        await self.channel.send(embed=vote_embed, view=view)
    
    async def end_game(self, winner):
        impostor_user = await bot.fetch_user(self.impostor)
        
        if winner == "crew":
            end_embed = discord.Embed(
                title="🎉 فاز المواطنون!",
                description=f"القاتل كان: {impostor_user.mention}\n\nأحسنتم! تم القبض على القاتل!",
                color=discord.Color.green()
            )
        else:
            end_embed = discord.Embed(
                title="🔪 فاز القاتل!",
                description=f"القاتل كان: {impostor_user.mention}\n\nالقاتل تمكن من قتل الجميع!",
                color=discord.Color.red()
            )
        
        await self.channel.send(embed=end_embed)

class ImpostorControlView(View):
    def __init__(self, game_manager):
        super().__init__(timeout=None)
        self.game_manager = game_manager
        
    @discord.ui.button(label="قتل لاعب", style=discord.ButtonStyle.danger, emoji="🔪")
    async def kill_player(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.game_manager.impostor:
            await interaction.response.send_message("أنت لست القاتل!", ephemeral=True)
            return
        
        # Create select menu for alive players
        options = []
        for player_id in self.game_manager.alive_players:
            if player_id != self.game_manager.impostor:
                user = await bot.fetch_user(player_id)
                options.append(discord.SelectOption(label=user.name, value=str(player_id)))
        
        if not options:
            await interaction.response.send_message("لا يوجد لاعبين للقتل!", ephemeral=True)
            return
        
        view = KillSelectView(self.game_manager, options)
        await interaction.response.send_message("اختر اللاعب الذي تريد قتله:", view=view, ephemeral=True)
    
    @discord.ui.button(label="إطفاء الأنوار", style=discord.ButtonStyle.secondary, emoji="💡")
    async def toggle_lights(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.game_manager.impostor:
            await interaction.response.send_message("أنت لست القاتل!", ephemeral=True)
            return
        
        self.game_manager.lights_on = not self.game_manager.lights_on
        status = "مضاءة" if self.game_manager.lights_on else "مطفأة"
        
        lights_embed = discord.Embed(
            title="💡 حالة الأنوار",
            description=f"الأنوار الآن: **{status}**",
            color=discord.Color.yellow() if self.game_manager.lights_on else discord.Color.dark_grey()
        )
        await self.game_manager.channel.send(embed=lights_embed)
        await interaction.response.send_message(f"تم! الأنوار الآن {status}", ephemeral=True)

class KillSelectView(View):
    def __init__(self, game_manager, options):
        super().__init__(timeout=30)
        self.game_manager = game_manager
        select = Select(placeholder="اختر اللاعب...", options=options)
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        victim_id = int(interaction.data['values'][0])
        await interaction.response.send_message("تم القتل!", ephemeral=True)
        await self.game_manager.kill_player(victim_id, interaction)
        self.stop()

class VotingView(View):
    def __init__(self, game_manager):
        super().__init__(timeout=60)
        self.game_manager = game_manager
        self.votes = {}
        self.add_voting_select()
    
    def add_voting_select(self):
        options = []
        for player_id in self.game_manager.alive_players:
            user = bot.get_user(player_id)
            if user:
                options.append(discord.SelectOption(label=user.name, value=str(player_id)))
        
        options.append(discord.SelectOption(label="تخطي التصويت", value="skip", emoji="⏭️"))
        
        select = Select(placeholder="صوت على من تشك به...", options=options)
        select.callback = self.vote_callback
        self.add_item(select)
    
    async def vote_callback(self, interaction: discord.Interaction):
        voter_id = interaction.user.id
        
        if voter_id not in self.game_manager.alive_players:
            await interaction.response.send_message("أنت ميت! لا يمكنك التصويت!", ephemeral=True)
            return
        
        voted_for = interaction.data['values'][0]
        self.votes[voter_id] = voted_for
        
        await interaction.response.send_message("تم تسجيل صوتك! ✅", ephemeral=True)
        
        # Check if all alive players voted
        if len(self.votes) >= len(self.game_manager.alive_players):
            await self.tally_votes()
    
    async def tally_votes(self):
        vote_counts = {}
        for vote in self.votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        # Find player with most votes
        if not vote_counts or max(vote_counts.values()) == vote_counts.get("skip", 0):
            result_embed = discord.Embed(
                title="⏭️ تم تخطي التصويت",
                description="لم يتم طرد أحد!",
                color=discord.Color.light_grey()
            )
            await self.game_manager.channel.send(embed=result_embed)
        else:
            ejected_id = max((k for k in vote_counts if k != "skip"), 
                           key=lambda k: vote_counts.get(k, 0), default=None)
            
            if ejected_id and ejected_id != "skip":
                ejected_id = int(ejected_id)
                ejected_user = await bot.fetch_user(ejected_id)
                
                if ejected_id in self.game_manager.alive_players:
                    self.game_manager.alive_players.remove(ejected_id)
                    self.game_manager.dead_players.append(ejected_id)
                
                was_impostor = ejected_id == self.game_manager.impostor
                role = "القاتل" if was_impostor else "مواطن بريء"
                
                result_embed = discord.Embed(
                    title="🚪 تم الطرد!",
                    description=f"**{ejected_user.mention}** تم طرده!\n\nكان: **{role}**",
                    color=discord.Color.red() if was_impostor else discord.Color.orange()
                )
                await self.game_manager.channel.send(embed=result_embed)
                
                # Check win condition
                winner = self.game_manager.check_win_condition()
                if winner:
                    await self.game_manager.end_game(winner)
        
        self.stop()

async def start_among_us_game(interaction: discord.Interaction):
    game_manager = AmongUsGameManager(interaction.channel, interaction.user.id)
    game_manager.players.append(interaction.user.id)
    
    embed = discord.Embed(
        title="🔪 لعبة بيننا",
        description=f"**عدد اللاعبين:** 1\n\nاضغط 'انضم للعبة' للمشاركة!",
        color=discord.Color.red()
    )
    
    view = AmongUsJoinView(game_manager)
    await interaction.channel.send(embed=embed, view=view)

# ================== Mafia Game ==================
class MafiaJoinView(View):
    def __init__(self, game_manager):
        super().__init__(timeout=60)
        self.game_manager = game_manager
        
    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.green, emoji="✅")
    async def join_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id in self.game_manager.players:
            await interaction.response.send_message("أنت مشترك بالفعل في اللعبة!", ephemeral=True)
        else:
            self.game_manager.players.append(interaction.user.id)
            await interaction.response.send_message("تم الانضمام بنجاح! 🎮", ephemeral=True)
            
            embed = discord.Embed(
                title="🕵️ لعبة المافيا",
                description=f"**عدد اللاعبين:** {len(self.game_manager.players)}\n\nانتظر حتى يبدأ منظم اللعبة!",
                color=discord.Color.dark_red()
            )
            await interaction.message.edit(embed=embed)
    
    @discord.ui.button(label="ابدأ اللعبة", style=discord.ButtonStyle.blurple, emoji="▶️")
    async def start_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.game_manager.starter_id:
            await interaction.response.send_message("فقط من بدأ اللعبة يمكنه تشغيلها!", ephemeral=True)
            return
            
        if len(self.game_manager.players) < 4:
            await interaction.response.send_message("يجب أن يكون هناك 4 لاعبين على الأقل!", ephemeral=True)
            return
        
        await interaction.response.send_message("جاري بدء اللعبة...", ephemeral=True)
        self.stop()
        await self.game_manager.start_game()

class MafiaGameManager:
    def __init__(self, channel, starter_id):
        self.channel = channel
        self.starter_id = starter_id
        self.players: List[int] = []
        self.mafia: List[int] = []
        self.doctor = None
        self.detective = None
        self.alive_players = []
        self.dead_players = []
        self.phase = "night"
        self.night_actions = {}
        
    async def start_game(self):
        self.alive_players = self.players.copy()
        
        # Assign roles
        num_mafia = max(1, len(self.players) // 4)
        self.mafia = random.sample(self.players, num_mafia)
        
        remaining = [p for p in self.players if p not in self.mafia]
        self.doctor = random.choice(remaining) if len(remaining) > 0 else None
        
        remaining = [p for p in remaining if p != self.doctor]
        self.detective = random.choice(remaining) if len(remaining) > 0 else None
        
        # Send roles
        for player_id in self.players:
            user = await bot.fetch_user(player_id)
            
            if player_id in self.mafia:
                mafia_members = [f"<@{m}>" for m in self.mafia if m != player_id]
                embed = discord.Embed(
                    title="🔫 دورك: مافيا",
                    description=f"أنت من المافيا!\n\n**أعضاء المافيا الآخرون:** {', '.join(mafia_members) if mafia_members else 'أنت وحدك'}",
                    color=discord.Color.dark_red()
                )
                await self.channel.send(f"{user.mention}", embed=embed, delete_after=0.1)
                
            elif player_id == self.doctor:
                embed = discord.Embed(
                    title="💊 دورك: الطبيب",
                    description="أنت الطبيب! يمكنك إنقاذ شخص واحد كل ليلة.",
                    color=discord.Color.green()
                )
                await self.channel.send(f"{user.mention}", embed=embed, delete_after=0.1)
                
            elif player_id == self.detective:
                embed = discord.Embed(
                    title="🔍 دورك: المحقق",
                    description="أنت المحقق! يمكنك التحقق من شخص واحد كل ليلة.",
                    color=discord.Color.blue()
                )
                await self.channel.send(f"{user.mention}", embed=embed, delete_after=0.1)
                
            else:
                embed = discord.Embed(
                    title="👤 دورك: مواطن",
                    description="أنت مواطن عادي. حاول البقاء على قيد الحياة!",
                    color=discord.Color.light_grey()
                )
                await self.channel.send(f"{user.mention}", embed=embed, delete_after=0.1)
        
        await self.night_phase()
    
    async def night_phase(self):
        self.phase = "night"
        self.night_actions = {}
        
        night_embed = discord.Embed(
            title="🌙 المرحلة الليلية",
            description="حل الظلام... المافيا تستيقظ!",
            color=discord.Color.dark_blue()
        )
        await self.channel.send(embed=night_embed)
        
        # Mafia action
        for mafia_id in self.mafia:
            if mafia_id in self.alive_players:
                user = await bot.fetch_user(mafia_id)
                options = [discord.SelectOption(label=(await bot.fetch_user(p)).name, value=str(p)) 
                          for p in self.alive_players if p not in self.mafia]
                
                if options:
                    view = MafiaKillView(self, options, mafia_id)
                    await self.channel.send(f"{user.mention} اختر من تريد قتله:", view=view, delete_after=0.1)
                break
        
        # Doctor action
        if self.doctor and self.doctor in self.alive_players:
            user = await bot.fetch_user(self.doctor)
            options = [discord.SelectOption(label=(await bot.fetch_user(p)).name, value=str(p)) 
                      for p in self.alive_players]
            
            view = DoctorSaveView(self, options)
            await self.channel.send(f"{user.mention} اختر من تريد إنقاذه:", view=view, delete_after=0.1)
        
        # Detective action
        if self.detective and self.detective in self.alive_players:
            user = await bot.fetch_user(self.detective)
            options = [discord.SelectOption(label=(await bot.fetch_user(p)).name, value=str(p)) 
                      for p in self.alive_players if p != self.detective]
            
            view = DetectiveInvestigateView(self, options)
            await self.channel.send(f"{user.mention} اختر من تريد التحقيق عنه:", view=view, delete_after=0.1)
        
        # Wait for actions
        await asyncio.sleep(30)
        await self.resolve_night()
    
    async def resolve_night(self):
        killed = self.night_actions.get('mafia_kill')
        saved = self.night_actions.get('doctor_save')
        
        if killed and killed != saved:
            self.alive_players.remove(killed)
            self.dead_players.append(killed)
            
            victim = await bot.fetch_user(killed)
            death_embed = discord.Embed(
                title="💀 تم العثور على جثة!",
                description=f"**{victim.mention}** تم قتله الليلة الماضية!",
                color=discord.Color.dark_red()
            )
            await self.channel.send(embed=death_embed)
        elif killed and killed == saved:
            saved_embed = discord.Embed(
                title="💊 تم الإنقاذ!",
                description="الطبيب نجح في إنقاذ الضحية!",
                color=discord.Color.green()
            )
            await self.channel.send(embed=saved_embed)
        else:
            safe_embed = discord.Embed(
                title="🌅 ليلة هادئة",
                description="لم يمت أحد الليلة الماضية!",
                color=discord.Color.gold()
            )
            await self.channel.send(embed=safe_embed)
        
        # Check win
        if await self.check_win():
            return
        
        await self.day_phase()
    
    async def day_phase(self):
        self.phase = "day"
        
        day_embed = discord.Embed(
            title="☀️ المرحلة النهارية",
            description="حان وقت المناقشة والتصويت!\n\n**اللاعبون الأحياء:** " + 
                       ", ".join([f"<@{p}>" for p in self.alive_players]),
            color=discord.Color.gold()
        )
        
        options = [discord.SelectOption(label=(await bot.fetch_user(p)).name, value=str(p)) 
                  for p in self.alive_players]
        options.append(discord.SelectOption(label="تخطي التصويت", value="skip", emoji="⏭️"))
        
        view = MafiaVotingView(self, options)
        await self.channel.send(embed=day_embed, view=view)
    
    async def check_win(self):
        mafia_alive = len([m for m in self.mafia if m in self.alive_players])
        citizens_alive = len(self.alive_players) - mafia_alive
        
        if mafia_alive == 0:
            embed = discord.Embed(
                title="🎉 فاز المواطنون!",
                description="تم القضاء على جميع أعضاء المافيا!",
                color=discord.Color.green()
            )
            await self.channel.send(embed=embed)
            return True
        elif mafia_alive >= citizens_alive:
            embed = discord.Embed(
                title="🔫 فازت المافيا!",
                description="المافيا سيطرت على المدينة!",
                color=discord.Color.dark_red()
            )
            await self.channel.send(embed=embed)
            return True
        
        return False

class MafiaKillView(View):
    def __init__(self, game_manager, options, mafia_id):
        super().__init__(timeout=25)
        self.game_manager = game_manager
        self.mafia_id = mafia_id
        select = Select(placeholder="اختر الضحية...", options=options)
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.mafia_id:
            await interaction.response.send_message("ليس دورك!", ephemeral=True)
            return
        
        victim_id = int(interaction.data['values'][0])
        self.game_manager.night_actions['mafia_kill'] = victim_id
        await interaction.response.send_message("تم تسجيل اختيارك!", ephemeral=True)
        self.stop()

class DoctorSaveView(View):
    def __init__(self, game_manager, options):
        super().__init__(timeout=25)
        self.game_manager = game_manager
        select = Select(placeholder="اختر من تريد إنقاذه...", options=options)
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.game_manager.doctor:
            await interaction.response.send_message("أنت لست الطبيب!", ephemeral=True)
            return
        
        saved_id = int(interaction.data['values'][0])
        self.game_manager.night_actions['doctor_save'] = saved_id
        await interaction.response.send_message("تم تسجيل اختيارك!", ephemeral=True)
        self.stop()

class DetectiveInvestigateView(View):
    def __init__(self, game_manager, options):
        super().__init__(timeout=25)
        self.game_manager = game_manager
        select = Select(placeholder="اختر من تريد التحقيق عنه...", options=options)
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.game_manager.detective:
            await interaction.response.send_message("أنت لست المحقق!", ephemeral=True)
            return
        
        investigated_id = int(interaction.data['values'][0])
        is_mafia = investigated_id in self.game_manager.mafia
        
        result = "مافيا" if is_mafia else "بريء"
        await interaction.response.send_message(f"نتيجة التحقيق: **{result}**", ephemeral=True)
        self.stop()

class MafiaVotingView(View):
    def __init__(self, game_manager, options):
        super().__init__(timeout=60)
        self.game_manager = game_manager
        self.votes = {}
        select = Select(placeholder="صوت على من تشك به...", options=options)
        select.callback = self.vote_callback
        self.add_item(select)
    
    async def vote_callback(self, interaction: discord.Interaction):
        if interaction.user.id not in self.game_manager.alive_players:
            await interaction.response.send_message("أنت ميت! لا يمكنك التصويت!", ephemeral=True)
            return
        
        voted_for = interaction.data['values'][0]
        self.votes[interaction.user.id] = voted_for
        await interaction.response.send_message("تم تسجيل صوتك! ✅", ephemeral=True)
        
        if len(self.votes) >= len(self.game_manager.alive_players):
            await self.tally_votes()
    
    async def tally_votes(self):
        vote_counts = {}
        for vote in self.votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        if not vote_counts or max(vote_counts.values()) == vote_counts.get("skip", 0):
            skip_embed = discord.Embed(
                title="⏭️ تم تخطي التصويت",
                description="لم يتم طرد أحد!",
                color=discord.Color.light_grey()
            )
            await self.game_manager.channel.send(embed=skip_embed)
        else:
            lynched_id = max((k for k in vote_counts if k != "skip"), 
                           key=lambda k: vote_counts.get(k, 0), default=None)
            
            if lynched_id and lynched_id != "skip":
                lynched_id = int(lynched_id)
                lynched_user = await bot.fetch_user(lynched_id)
                
                if lynched_id in self.game_manager.alive_players:
                    self.game_manager.alive_players.remove(lynched_id)
                    self.game_manager.dead_players.append(lynched_id)
                
                role = "مافيا" if lynched_id in self.game_manager.mafia else "مواطن بريء"
                
                lynch_embed = discord.Embed(
                    title="🚪 تم الإعدام!",
                    description=f"**{lynched_user.mention}** تم إعدامه!\n\nكان: **{role}**",
                    color=discord.Color.red()
                )
                await self.game_manager.channel.send(embed=lynch_embed)
        
        # Check win
        if await self.game_manager.check_win():
            self.stop()
            return
        
        await self.game_manager.night_phase()
        self.stop()

async def start_mafia_game(interaction: discord.Interaction):
    game_manager = MafiaGameManager(interaction.channel, interaction.user.id)
    game_manager.players.append(interaction.user.id)
    
    embed = discord.Embed(
        title="🕵️ لعبة المافيا",
        description=f"**عدد اللاعبين:** 1\n\nاضغط 'انضم للعبة' للمشاركة!\n\n**الحد الأدنى:** 4 لاعبين",
        color=discord.Color.dark_red()
    )
    
    view = MafiaJoinView(game_manager)
    await interaction.channel.send(embed=embed, view=view)

# ================== Roulette Game ==================
class RouletteJoinView(View):
    def __init__(self, game_manager):
        super().__init__(timeout=60)
        self.game_manager = game_manager
        
    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.green, emoji="✅")
    async def join_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id in self.game_manager.players:
            await interaction.response.send_message("أنت مشترك بالفعل في اللعبة!", ephemeral=True)
        else:
            self.game_manager.players.append(interaction.user.id)
            await interaction.response.send_message("تم الانضمام بنجاح! 🎮", ephemeral=True)
            
            embed = discord.Embed(
                title="🎡 لعبة الروليت",
                description=f"**عدد اللاعبين:** {len(self.game_manager.players)}\n\nانتظر حتى يبدأ منظم اللعبة!",
                color=discord.Color.purple()
            )
            await interaction.message.edit(embed=embed)
    
    @discord.ui.button(label="ابدأ اللعبة", style=discord.ButtonStyle.blurple, emoji="▶️")
    async def start_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.game_manager.starter_id:
            await interaction.response.send_message("فقط من بدأ اللعبة يمكنه تشغيلها!", ephemeral=True)
            return
            
        if len(self.game_manager.players) < 3:
            await interaction.response.send_message("يجب أن يكون هناك 3 لاعبين على الأقل!", ephemeral=True)
            return
        
        await interaction.response.send_message("جاري بدء اللعبة...", ephemeral=True)
        self.stop()
        await self.game_manager.start_game()

class RouletteGameManager:
    def __init__(self, channel, starter_id):
        self.channel = channel
        self.starter_id = starter_id
        self.players: List[int] = []
        self.alive_players = []
        
    async def start_game(self):
        self.alive_players = self.players.copy()
        
        start_embed = discord.Embed(
            title="🎡 بدأت لعبة الروليت!",
            description=f"**عدد اللاعبين:** {len(self.players)}\n\nآخر لاعب يبقى على قيد الحياة يفوز!",
            color=discord.Color.purple()
        )
        await self.channel.send(embed=start_embed)
        
        await self.spin_wheel()
    
    async def spin_wheel(self):
        if len(self.alive_players) <= 1:
            winner_id = self.alive_players[0] if self.alive_players else None
            if winner_id:
                winner = await bot.fetch_user(winner_id)
                win_embed = discord.Embed(
                    title="🎉 فائز!",
                    description=f"**{winner.mention}** هو آخر لاعب متبقي!\n\n**الفائز بلعبة الروليت!**",
                    color=discord.Color.gold()
                )
                await self.channel.send(embed=win_embed)
            return
        
        # Spinning animation
        spin_embed = discord.Embed(
            title="🎡 العجلة تدور...",
            description="⭕ 🔄 ⭕ 🔄 ⭕",
            color=discord.Color.purple()
        )
        spin_msg = await self.channel.send(embed=spin_embed)
        
        await asyncio.sleep(2)
        
        # Select random player
        selected_player = random.choice(self.alive_players)
        selected_user = await bot.fetch_user(selected_player)
        
        result_embed = discord.Embed(
            title="🎯 توقفت العجلة!",
            description=f"**{selected_user.mention}** تم اختياره!\n\nالآن يجب أن يختار لاعباً للإقصاء!",
            color=discord.Color.red()
        )
        await spin_msg.edit(embed=result_embed)
        
        # Let selected player choose who to eliminate
        options = []
        for player_id in self.alive_players:
            if player_id != selected_player:
                user = await bot.fetch_user(player_id)
                options.append(discord.SelectOption(label=user.name, value=str(player_id)))
        
        if not options:
            # Only one player left
            await self.spin_wheel()
            return
        
        view = RouletteEliminateView(self, options, selected_player)
        await self.channel.send(f"{selected_user.mention} اختر من تريد إقصاءه:", view=view)
    
    async def eliminate_player(self, eliminated_id):
        if eliminated_id in self.alive_players:
            self.alive_players.remove(eliminated_id)
        
        eliminated_user = await bot.fetch_user(eliminated_id)
        
        elim_embed = discord.Embed(
            title="💀 تم الإقصاء!",
            description=f"**{eliminated_user.mention}** خرج من اللعبة!\n\n**اللاعبون المتبقون:** {len(self.alive_players)}",
            color=discord.Color.dark_red()
        )
        await self.channel.send(embed=elim_embed)
        
        await asyncio.sleep(3)
        await self.spin_wheel()

class RouletteEliminateView(View):
    def __init__(self, game_manager, options, selector_id):
        super().__init__(timeout=30)
        self.game_manager = game_manager
        self.selector_id = selector_id
        select = Select(placeholder="اختر من تريد إقصاءه...", options=options)
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.selector_id:
            await interaction.response.send_message("ليس دورك!", ephemeral=True)
            return
        
        eliminated_id = int(interaction.data['values'][0])
        await interaction.response.send_message("تم تسجيل اختيارك!", ephemeral=True)
        self.stop()
        await self.game_manager.eliminate_player(eliminated_id)

async def start_roulette_game(interaction: discord.Interaction):
    game_manager = RouletteGameManager(interaction.channel, interaction.user.id)
    game_manager.players.append(interaction.user.id)
    
    embed = discord.Embed(
        title="🎡 لعبة الروليت",
        description=f"**عدد اللاعبين:** 1\n\nاضغط 'انضم للعبة' للمشاركة!\n\n**الحد الأدنى:** 3 لاعبين",
        color=discord.Color.purple()
    )
    
    view = RouletteJoinView(game_manager)
    await interaction.channel.send(embed=embed, view=view)

# ================== Bot Commands ==================
@bot.command(name="ألعاب")
async def games_command(ctx):
    embed = discord.Embed(
        title="هذه هي ألعاب هذا البوت",
        description="اختر الفئة المناسبة من القائمة أدناه:",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="⚡ ألعاب فردية",
        value="ألعاب سريعة وتحديات فردية",
        inline=True
    )
    embed.add_field(
        name="👥 ألعاب جماعية",
        value="ألعاب حفلات وتحديات جماعية",
        inline=True
    )
    embed.set_footer(text="استمتع باللعب! 🎮")
    
    view = MainMenuView()
    await ctx.send(embed=embed, view=view)

@bot.command(name="نقاطي")
async def my_score(ctx):
    score = user_scores.get(ctx.author.id, 0)
    embed = discord.Embed(
        title="📊 نقاطك",
        description=f"**{ctx.author.mention}**\n\nالنقاط الكلية: **{score}**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="المتصدرين")
async def leaderboard(ctx):
    if not user_scores:
        await ctx.send("لا توجد نقاط مسجلة بعد!")
        return
    
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 لوحة المتصدرين",
        description="أفضل 10 لاعبين:",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (user_id, score) in enumerate(sorted_scores):
        user = await bot.fetch_user(user_id)
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        embed.add_field(
            name=f"{medal} {user.name}",
            value=f"النقاط: {score}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ البوت جاهز! تم تسجيل الدخول باسم: {bot.user}")
    print(f"🎮 البوت موجود في {len(bot.guilds)} سيرفر")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=".ألعاب | ألعاب عربية ممتعة!"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ ينقص معامل: {error.param}")
    else:
        print(f"خطأ: {error}")
        await ctx.send("❌ حدث خطأ أثناء تنفيذ الأمر!")

# ================== Run Bot ==================
if __name__ == "__main__":
    TOKEN = "MTQwNTI5NjYyMTc1MDg0NTU1Mg.GPqbXp.IVjFl8_1xL-Qakjfb8ToSnOF1W7jj4xvu9j1dY"
    bot.run(TOKEN)
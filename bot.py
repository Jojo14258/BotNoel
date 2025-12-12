"""
Bot Discord de Noël - Point d'entrée principal
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from modules.config import DISCORD_TOKEN, CHANNEL_ID, CHRISTMAS_TREE_EMOJI
from modules.gift_manager import GiftManager
import modules.config as config


class ChristmasBot(commands.Bot):
    """Bot Discord pour le jeu de cadeaux de Noël"""
    
    def __init__(self):
        # Définir les intents nécessaires
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.gift_manager = None
        
    async def setup_hook(self):
        """Configuration initiale du bot"""
        print("Configuration du bot...")
        self.gift_manager = GiftManager(self)
        
        # Synchroniser les commandes slash
        await self.tree.sync()
        print("Commandes slash synchronisées !")
        
    async def on_ready(self):
        """Appelé quand le bot est prêt"""
        print(f'{CHRISTMAS_TREE_EMOJI} Bot connecté en tant que {self.user}')
        print(f'ID: {self.user.id}')
        print('------')
        
        # Définir le statut du bot
        await self.change_presence(
            activity=discord.Game(name="🎁 Jeu de cadeaux de Noël")
        )


# Créer l'instance du bot
bot = ChristmasBot()


# ==================== COMMANDES SLASH ====================

@bot.tree.command(name="start", description="Démarre le jeu de cadeaux de Noël")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(channel="Canal où faire apparaître les cadeaux (optionnel)")
async def slash_start(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Démarre le jeu de cadeaux de Noël"""
    if bot.gift_manager.is_running:
        await interaction.response.send_message("🎄 Le jeu est déjà en cours !", ephemeral=True)
        return
    
    # Utiliser le canal spécifié, sinon le canal configuré, sinon le canal actuel
    target_channel = channel or bot.get_channel(CHANNEL_ID) or interaction.channel
    
    # Démarrer la boucle d'apparition des cadeaux
    bot.loop.create_task(bot.gift_manager.start_spawn_loop(target_channel))
    
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Jeu de Noël démarré !",
        description=f"Les cadeaux vont commencer à apparaître dans {target_channel.mention} !\n\n"
                   f"🎁 Soyez rapides pour les récupérer !\n"
                   f"⭐ Tentez de gagner le rôle spécial de Noël !",
        color=0x00FF00
    )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stop", description="Arrête le jeu de cadeaux de Noël")
@app_commands.default_permissions(administrator=True)
async def slash_stop(interaction: discord.Interaction):
    """Arrête le jeu de cadeaux de Noël"""
    if not bot.gift_manager.is_running:
        await interaction.response.send_message("🎄 Le jeu n'est pas en cours.", ephemeral=True)
        return
    
    bot.gift_manager.stop_spawn_loop()
    
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Jeu de Noël arrêté",
        description="Le jeu a été arrêté. Plus aucun cadeau n'apparaîtra.",
        color=0xFF0000
    )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="config", description="Configure les paramètres du jeu")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    gift_lifetime="Durée de vie d'un cadeau en secondes",
    min_interval="Intervalle minimum entre cadeaux (secondes)",
    max_interval="Intervalle maximum entre cadeaux (secondes)",
    win_probability="Probabilité de gagner (0.0 à 1.0)"
)
async def slash_config(
    interaction: discord.Interaction,
    gift_lifetime: int = None,
    min_interval: int = None,
    max_interval: int = None,
    win_probability: float = None
):
    """Configure les paramètres du jeu"""
    changes = []
    
    if gift_lifetime is not None:
        if gift_lifetime < 1 or gift_lifetime > 60:
            await interaction.response.send_message("❌ La durée de vie doit être entre 1 et 60 secondes.", ephemeral=True)
            return
        config.GIFT_LIFETIME = gift_lifetime
        changes.append(f"• Durée de vie des cadeaux: **{gift_lifetime}s**")
    
    if min_interval is not None:
        if min_interval < 1:
            await interaction.response.send_message("❌ L'intervalle minimum doit être au moins 1 seconde.", ephemeral=True)
            return
        config.MIN_SPAWN_INTERVAL = min_interval
        changes.append(f"• Intervalle minimum: **{min_interval}s** ({min_interval//60} min)")
    
    if max_interval is not None:
        if max_interval < config.MIN_SPAWN_INTERVAL:
            await interaction.response.send_message("❌ L'intervalle maximum doit être supérieur au minimum.", ephemeral=True)
            return
        config.MAX_SPAWN_INTERVAL = max_interval
        changes.append(f"• Intervalle maximum: **{max_interval}s** ({max_interval//60} min)")
    
    if win_probability is not None:
        if win_probability < 0 or win_probability > 1:
            await interaction.response.send_message("❌ La probabilité doit être entre 0.0 et 1.0.", ephemeral=True)
            return
        config.WIN_PROBABILITY = win_probability
        changes.append(f"• Probabilité de gagner: **{win_probability*100:.1f}%**")
    
    if not changes:
        # Afficher la configuration actuelle
        embed = discord.Embed(
            title="⚙️ Configuration actuelle",
            color=0x3498db
        )
        embed.add_field(
            name="Paramètres du jeu",
            value=f"• Durée de vie des cadeaux: **{config.GIFT_LIFETIME}s**\n"
                  f"• Intervalle minimum: **{config.MIN_SPAWN_INTERVAL}s** ({config.MIN_SPAWN_INTERVAL//60} min)\n"
                  f"• Intervalle maximum: **{config.MAX_SPAWN_INTERVAL}s** ({config.MAX_SPAWN_INTERVAL//60} min)\n"
                  f"• Probabilité de gagner: **{config.WIN_PROBABILITY*100:.1f}%**",
            inline=False
        )
        await interaction.response.send_message(embed=embed)
    else:
        # Afficher les changements
        embed = discord.Embed(
            title="✅ Configuration mise à jour",
            description="\n".join(changes),
            color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="info", description="Affiche les informations sur le jeu")
async def slash_info(interaction: discord.Interaction):
    """Affiche les informations sur le jeu"""
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Jeu de Cadeaux de Noël",
        description="Voici comment jouer :",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎁 Comment jouer ?",
        value=f"Des cadeaux apparaissent aléatoirement dans le chat !\n"
              f"Soyez le premier à cliquer sur le bouton pour tenter votre chance.",
        inline=False
    )
    
    embed.add_field(
        name="⏱️ Timing",
        value=f"• Cadeaux visibles pendant **{config.GIFT_LIFETIME} secondes**\n"
              f"• Apparition toutes les **{config.MIN_SPAWN_INTERVAL//60}-{config.MAX_SPAWN_INTERVAL//60} minutes**",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Récompenses",
        value=f"• **{config.WIN_PROBABILITY*100:.0f}%** de chance de gagner un rôle spécial\n"
              f"• Sinon, découvrez un fun fact sur Noël !",
        inline=False
    )
    
    status = "✅ En cours" if bot.gift_manager.is_running else "❌ Arrêté"
    embed.add_field(
        name="📊 Statut",
        value=status,
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Affiche l'aide des commandes")
async def slash_help(interaction: discord.Interaction):
    """Affiche l'aide des commandes"""
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Commandes du Bot de Noël",
        description="Liste des commandes disponibles :",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎮 Commandes pour tous",
        value="</info:0> - Affiche les informations sur le jeu\n"
              "</help:0> - Affiche cette aide",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Commandes administrateur",
        value="</start:0> - Démarre le jeu de cadeaux\n"
              "</stop:0> - Arrête le jeu de cadeaux\n"
              "</config:0> - Configure les paramètres du jeu",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==================== COMMANDES PRÉFIXE (!) ====================

@bot.command(name='start')
@commands.has_permissions(administrator=True)
async def start_game(ctx):
    """
    Démarre le jeu de cadeaux de Noël
    Commande réservée aux administrateurs
    """
    if bot.gift_manager.is_running:
        await ctx.send("🎄 Le jeu est déjà en cours !")
        return
        
    # Récupérer le canal configuré ou utiliser le canal actuel
    channel_id = CHANNEL_ID if CHANNEL_ID != 0 else ctx.channel.id
    channel = bot.get_channel(channel_id)
    
    if channel is None:
        await ctx.send("❌ Canal introuvable ! Vérifiez la configuration.")
        return
        
    # Démarrer la boucle d'apparition des cadeaux
    bot.loop.create_task(bot.gift_manager.start_spawn_loop(channel))
    
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Jeu de Noël démarré !",
        description=f"Les cadeaux vont commencer à apparaître dans {channel.mention} !\n\n"
                   f"🎁 Soyez rapides pour les récupérer !\n"
                   f"⭐ Tentez de gagner le rôle spécial de Noël !",
        color=0x00FF00
    )
    
    await ctx.send(embed=embed)


@bot.command(name='stop')
@commands.has_permissions(administrator=True)
async def stop_game(ctx):
    """
    Arrête le jeu de cadeaux de Noël
    Commande réservée aux administrateurs
    """
    if not bot.gift_manager.is_running:
        await ctx.send("🎄 Le jeu n'est pas en cours.")
        return
        
    bot.gift_manager.stop_spawn_loop()
    
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Jeu de Noël arrêté",
        description="Le jeu a été arrêté. Plus aucun cadeau n'apparaîtra.",
        color=0xFF0000
    )
    
    await ctx.send(embed=embed)


@bot.command(name='info')
async def game_info(ctx):
    """Affiche les informations sur le jeu"""
    from modules.config import GIFT_LIFETIME, MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL, WIN_PROBABILITY
    
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Jeu de Cadeaux de Noël",
        description="Voici comment jouer :",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎁 Comment jouer ?",
        value=f"Des cadeaux apparaissent aléatoirement dans le chat !\n"
              f"Soyez le premier à cliquer sur le bouton pour tenter votre chance.",
        inline=False
    )
    
    embed.add_field(
        name="⏱️ Timing",
        value=f"• Cadeaux visibles pendant **{GIFT_LIFETIME} secondes**\n"
              f"• Apparition toutes les **{MIN_SPAWN_INTERVAL//60}-{MAX_SPAWN_INTERVAL//60} minutes**",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Récompenses",
        value=f"• **{WIN_PROBABILITY*100:.0f}%** de chance de gagner un rôle spécial\n"
              f"• Sinon, découvrez un fun fact sur Noël !",
        inline=False
    )
    
    status = "✅ En cours" if bot.gift_manager.is_running else "❌ Arrêté"
    embed.add_field(
        name="📊 Statut",
        value=status,
        inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command(name='help')
async def help_command(ctx):
    """Affiche l'aide des commandes"""
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Commandes du Bot de Noël",
        description="Utilisez les commandes slash `/` ou préfixe `!`",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎮 Pour tous",
        value="`/info` ou `!info` - Informations sur le jeu\n"
              "`/help` ou `!help` - Cette aide",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Admin uniquement",
        value="`/start` ou `!start` - Démarrer le jeu\n"
              "`/stop` ou `!stop` - Arrêter le jeu\n"
              "`/config` - Configurer le jeu",
        inline=False
    )
    
    await ctx.send(embed=embed)


# Gestion des erreurs
@start_game.error
@stop_game.error
async def permission_error(ctx, error):
    """Gère les erreurs de permission"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous devez être administrateur pour utiliser cette commande !")


def main():
    """Point d'entrée principal"""
    if not DISCORD_TOKEN:
        print("❌ ERREUR : Le token Discord n'est pas configuré !")
        print("Veuillez créer un fichier .env avec votre DISCORD_TOKEN")
        return
        
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ ERREUR : Token Discord invalide !")
    except Exception as e:
        print(f"❌ ERREUR : {e}")


if __name__ == "__main__":
    main()

"""
Bot Discord de Noël - Point d'entrée principal
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import os
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
            command_prefix='*',
            intents=intents,
            help_command=None,
            application_id=None  # Désactive l'installation en tant qu'application utilisateur
        )
        
        self.gift_manager = None
        self.admin_whitelist = self._load_admin_whitelist()
        
    def _load_admin_whitelist(self):
        """Charge la liste des IDs Discord autorisés à utiliser les commandes admin"""
        whitelist_file = os.path.join(os.path.dirname(__file__), "data", "admin_whitelist.json")
        try:
            if os.path.exists(whitelist_file):
                with open(whitelist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('admins', [])
        except Exception as e:
            print(f"Erreur lors du chargement de la whitelist admin : {e}")
        return []
    
    def is_whitelisted_admin(self, user_id: int) -> bool:
        """Vérifie si l'utilisateur est dans la whitelist admin"""
        return user_id in self.admin_whitelist
        
    async def setup_hook(self):
        """Configuration initiale du bot"""
        print("Configuration du bot...")
        self.gift_manager = GiftManager(self)
        
        # Synchroniser les commandes slash globalement
        # Note: Peut prendre jusqu'à 1h pour se propager
        # Pour sync instantané sur un serveur spécifique, voir on_ready
        await self.tree.sync()
        print("Commandes slash synchronisées !")
        
    async def on_ready(self):
        """Appelé quand le bot est prêt"""
        print(f'{CHRISTMAS_TREE_EMOJI} Bot connecté en tant que {self.user}')
        print(f'ID: {self.user.id}')
        print('------')
        
        # Définir le statut du bot
        await self.change_presence(
            activity=discord.Game(name="🎁 Jeu de cadeaux de Noël (*info)")
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
    role_probability="Probabilité de gagner le rôle (0.0 à 1.0)",
    book_probability="Probabilité de gagner le livre (0.0 à 1.0)",
    log_channel="Canal pour les logs des gains",
    max_roles="Nombre max de rôles à distribuer (-1 = illimité)",
    max_books="Nombre max de livres à distribuer (-1 = illimité)"
)
async def slash_config(
    interaction: discord.Interaction,
    gift_lifetime: int = None,
    min_interval: int = None,
    max_interval: int = None,
    role_probability: float = None,
    book_probability: float = None,
    log_channel: discord.TextChannel = None,
    max_roles: int = None,
    max_books: int = None
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
    
    if role_probability is not None:
        if role_probability < 0 or role_probability > 1:
            await interaction.response.send_message("❌ La probabilité doit être entre 0.0 et 1.0.", ephemeral=True)
            return
        config.ROLE_PROBABILITY = role_probability
        changes.append(f"• Probabilité de gagner le rôle: **{role_probability*100:.1f}%**")
    
    if book_probability is not None:
        if book_probability < 0 or book_probability > 1:
            await interaction.response.send_message("❌ La probabilité doit être entre 0.0 et 1.0.", ephemeral=True)
            return
        config.BOOK_PROBABILITY = book_probability
        changes.append(f"• Probabilité de gagner le livre: **{book_probability*100:.1f}%**")
    
    if log_channel is not None:
        config.LOG_CHANNEL_ID = log_channel.id
        changes.append(f"• Canal de logs: {log_channel.mention}")
    
    if max_roles is not None:
        if max_roles < -1:
            await interaction.response.send_message("❌ Le nombre doit être -1 (illimité) ou positif.", ephemeral=True)
            return
        config.MAX_ROLES = max_roles
        changes.append(f"• Stock max de rôles: **{'∞' if max_roles == -1 else max_roles}**")
    
    if max_books is not None:
        if max_books < -1:
            await interaction.response.send_message("❌ Le nombre doit être -1 (illimité) ou positif.", ephemeral=True)
            return
        config.MAX_BOOKS = max_books
        changes.append(f"• Stock max de livres: **{'∞' if max_books == -1 else max_books}**")
    
    if not changes:
        # Afficher la configuration actuelle
        embed = discord.Embed(
            title="⚙️ Configuration actuelle",
            color=0x3498db
        )
        
        log_ch = interaction.guild.get_channel(config.LOG_CHANNEL_ID) if config.LOG_CHANNEL_ID else None
        
        roles_remaining = config.MAX_ROLES - config.ROLES_GIVEN if config.MAX_ROLES != -1 else "∞"
        books_remaining = config.MAX_BOOKS - config.BOOKS_GIVEN if config.MAX_BOOKS != -1 else "∞"
        
        embed.add_field(
            name="Paramètres du jeu",
            value=f"• Durée de vie des cadeaux: **{config.GIFT_LIFETIME}s**\n"
                  f"• Intervalle minimum: **{config.MIN_SPAWN_INTERVAL}s** ({config.MIN_SPAWN_INTERVAL//60} min)\n"
                  f"• Intervalle maximum: **{config.MAX_SPAWN_INTERVAL}s** ({config.MAX_SPAWN_INTERVAL//60} min)\n"
                  f"• Probabilité rôle: **{config.ROLE_PROBABILITY*100:.1f}%**\n"
                  f"• Probabilité livre: **{config.BOOK_PROBABILITY*100:.1f}%**\n"
                  f"• Canal de logs: {log_ch.mention if log_ch else '❌ Non configuré'}",
            inline=False
        )
        
        embed.add_field(
            name="📊 Stock de récompenses",
            value=f"🎅 Rôles: **{config.ROLES_GIVEN}** / **{'∞' if config.MAX_ROLES == -1 else config.MAX_ROLES}** (Restant: **{roles_remaining}**)\n"
                  f"📚 Livres: **{config.BOOKS_GIVEN}** / **{'∞' if config.MAX_BOOKS == -1 else config.MAX_BOOKS}** (Restant: **{books_remaining}**)",
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


@bot.tree.command(name="stock", description="Affiche le stock de récompenses restant")
@app_commands.default_permissions(administrator=True)
async def slash_stock(interaction: discord.Interaction):
    """Affiche le stock de récompenses restant"""
    roles_remaining = config.MAX_ROLES - config.ROLES_GIVEN if config.MAX_ROLES != -1 else "∞"
    books_remaining = config.MAX_BOOKS - config.BOOKS_GIVEN if config.MAX_BOOKS != -1 else "∞"
    
    embed = discord.Embed(
        title="📊 Stock de récompenses",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎅 Rôles",
        value=f"**Distribués :** {config.ROLES_GIVEN}\n"
              f"**Maximum :** {'∞' if config.MAX_ROLES == -1 else config.MAX_ROLES}\n"
              f"**Restant :** {roles_remaining}",
        inline=True
    )
    
    embed.add_field(
        name="📚 Livres",
        value=f"**Distribués :** {config.BOOKS_GIVEN}\n"
              f"**Maximum :** {'∞' if config.MAX_BOOKS == -1 else config.MAX_BOOKS}\n"
              f"**Restant :** {books_remaining}",
        inline=True
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


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
              f"Soyez le premier à cliquer sur le bouton pour tenter votre chance.\n"
              f"\u26a0️ Attention : les cadeaux disparaissent rapidement s'ils ne sont pas réclamés !",
        inline=False
    )
    
    # Afficher le salon si le jeu est en cours
    if bot.gift_manager.is_running and bot.gift_manager.channel:
        embed.add_field(
            name="📍 Salon des cadeaux",
            value=f"Les cadeaux apparaissent dans {bot.gift_manager.channel.mention}",
            inline=False
        )
    
    embed.add_field(
        name="🎯 Récompenses",
        value=f"• Tentez de gagner un rôle spécial de Noël ! 🎅\n"
              f"• Ou le livre 'Guide de survie au lycée' ! 📚\n"
              f"• Ou découvrez un fun fact sur Noël ! 🎄",
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
              "</config:0> - Configure les paramètres du jeu\n"
              "</stock:0> - Affiche le stock de récompenses restant\n\n"
              "**Ou utilisez le préfixe `*` :** `*start`, `*stop`, `*stock`, `*sync`",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==================== COMMANDES PRÉFIXE (*) ====================

@bot.command(name='start')
async def start_game(ctx):
    """
    Démarre le jeu de cadeaux de Noël
    Commande réservée aux administrateurs ou utilisateurs autorisés
    """
    # Vérifier si l'utilisateur est admin du serveur OU dans la whitelist
    if not (ctx.author.guild_permissions.administrator or bot.is_whitelisted_admin(ctx.author.id)):
        await ctx.send("❌ Vous devez être administrateur pour utiliser cette commande !")
        return
    
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
async def stop_game(ctx):
    """
    Arrête le jeu de cadeaux de Noël
    Commande réservée aux administrateurs ou utilisateurs autorisés
    """
    # Vérifier si l'utilisateur est admin du serveur OU dans la whitelist
    if not (ctx.author.guild_permissions.administrator or bot.is_whitelisted_admin(ctx.author.id)):
        await ctx.send("❌ Vous devez être administrateur pour utiliser cette commande !")
        return
    
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
    embed = discord.Embed(
        title=f"{CHRISTMAS_TREE_EMOJI} Jeu de Cadeaux de Noël",
        description="Voici comment jouer :",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎁 Comment jouer ?",
        value=f"Des cadeaux apparaissent aléatoirement dans le chat !\n"
              f"Soyez le premier à cliquer sur le bouton pour tenter votre chance.\n"
              f"\u26a0️ Attention : les cadeaux disparaissent rapidement s'ils ne sont pas réclamés !",
        inline=False
    )
    
    # Afficher le salon si le jeu est en cours
    if bot.gift_manager.is_running and bot.gift_manager.channel:
        embed.add_field(
            name="📍 Salon des cadeaux",
            value=f"Les cadeaux apparaissent dans {bot.gift_manager.channel.mention}",
            inline=False
        )
    
    embed.add_field(
        name="🎯 Récompenses",
        value=f"• Tentez de gagner un rôle spécial de Noël ! 🎅\n"
              f"• Ou le livre 'Guide de survie au lycée' ! 📚\n"
              f"• Ou découvrez un fun fact sur Noël ! 🎄",
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
        description="Utilisez les commandes slash `/` ou préfixe `*`",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎮 Pour tous",
        value="`/info` ou `*info` - Informations sur le jeu\n"
              "`/help` ou `*help` - Cette aide",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Admin uniquement",
        value="`/start` ou `*start` - Démarrer le jeu\n"
              "`/stop` ou `*stop` - Arrêter le jeu\n"
              "`/config` ou `*stock` - Configurer le jeu / Voir le stock\n"
              "`*sync` - Synchroniser les commandes slash",
        inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command(name='stock')
async def stock_command(ctx):
    """
    Affiche le stock de récompenses restant
    Commande réservée aux administrateurs ou utilisateurs autorisés
    """
    # Vérifier si l'utilisateur est admin du serveur OU dans la whitelist
    if not (ctx.author.guild_permissions.administrator or bot.is_whitelisted_admin(ctx.author.id)):
        await ctx.send("❌ Vous devez être administrateur pour utiliser cette commande !")
        return
    
    roles_remaining = config.MAX_ROLES - config.ROLES_GIVEN if config.MAX_ROLES != -1 else "∞"
    books_remaining = config.MAX_BOOKS - config.BOOKS_GIVEN if config.MAX_BOOKS != -1 else "∞"
    
    embed = discord.Embed(
        title="📊 Stock de récompenses",
        color=0x3498db
    )
    
    embed.add_field(
        name="🎅 Rôles",
        value=f"**Distribués :** {config.ROLES_GIVEN}\n"
              f"**Maximum :** {'∞' if config.MAX_ROLES == -1 else config.MAX_ROLES}\n"
              f"**Restant :** {roles_remaining}",
        inline=True
    )
    
    embed.add_field(
        name="📚 Livres",
        value=f"**Distribués :** {config.BOOKS_GIVEN}\n"
              f"**Maximum :** {'∞' if config.MAX_BOOKS == -1 else config.MAX_BOOKS}\n"
              f"**Restant :** {books_remaining}",
        inline=True
    )
    
    await ctx.send(embed=embed)


@bot.command(name='sync')
async def sync_commands(ctx):
    """Supprime toutes les commandes du serveur puis resynchronise"""
    # Vérifier si l'utilisateur est admin du serveur OU dans la whitelist
    if not (ctx.author.guild_permissions.administrator or bot.is_whitelisted_admin(ctx.author.id)):
        await ctx.send("❌ Vous devez être administrateur pour utiliser cette commande !")
        return
    
    try:
        guild = ctx.guild
        # Supprimer toutes les commandes spécifiques au serveur
        bot.tree.clear_commands(guild=guild)
        await bot.tree.sync(guild=guild)
        await ctx.send(f"🗑️ Commandes du serveur supprimées !")
        
        # Maintenant copier et synchroniser les commandes globales
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        await ctx.send(f"✅ {len(synced)} commandes resynchronisées pour ce serveur !")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de la synchronisation : {e}")


# Pas besoin de gestion d'erreur de permissions car on vérifie manuellement


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

"""
Script pour retirer tous les emojis du fichier server.py
Résout le problème UnicodeEncodeError sur Windows PowerShell
"""

import re

# Lire le fichier
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapping des emojis vers du texte simple
replacements = {
    '⚠️': '[WARNING]',
    '✅': '[OK]',
    '❌': '[ERROR]',
    '🚀': '[START]',
    '📊': '[DATABASE]',
    '💰': '[PAYMENT]',
    '🔗': '[TRACKING]',
    '📡': '[WEBHOOK]',
    '💳': '[GATEWAY]',
    '📄': '[INVOICE]',
    '⏰': '[SCHEDULER]',
    '🛑': '[STOP]',
    '📅': '[SCHEDULE]',
    '📱': '[2FA]',
    '🔍': '[SEARCH]'
}

# Remplacer tous les emojis
for emoji, text in replacements.items():
    content = content.replace(emoji, text)

# Sauvegarder
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK - Emojis supprimés de server.py")

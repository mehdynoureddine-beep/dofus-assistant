
Assistant Dofus Rétro - build
===========================

Fichiers générés :
- dofus_assistant.py : script principal
- README-build.txt : instructions pour construire l'exécutable sur Windows

Instructions rapides pour créer un .exe sur ta machine Windows :
1. Installe Python 3.10+ et pip.
2. Crée un environnement virtuel :
   python -m venv venv
   venv\Scripts\activate
3. Installe les dépendances :
   pip install openai pyinstaller
4. Copie dofus_assistant.py dans un dossier, puis exécute :
   pyinstaller --onefile --noconsole dofus_assistant.py
5. Récupère l'exécutable dans le dossier dist\

L'exécutable demandera une clé OpenAI si tu veux utiliser les fonctionnalités en ligne.

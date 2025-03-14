# IJVM-tools
### Vous galérez avec l'IJVM ? Voici quelques outils qui pourrons vous être utils


## Décompileur
Ce programme permet de transformer un texte représentant un code IJVM compilé en hexadécimal, en code IJVM lisible.

**Fichier:** `decompiler.py`
#### Utilisation:
**Fonction:** `decompile()`  
**Arguments:**  
| Argument       | Type  | Optionelle | Description |
|:---------------|:-----:|:-----------:|:------------|
| `bytecode`     | `str` | ❌         | Code hexadécimal correspondant au code IJVM. <br/> **Doit obligatoirement être adressé.**
| `constantPool` | `str` | ✔️         | Pool de constantes hexadécimal du code IJVM. <br/> **Doit obligatoirement être adressé.**
| `outputFile`   | `str` | ✔️         | Fichier vers lequel sera envoyer le résultat.
| `format`       | `str` | ✔️         | **/!\ Non implémenté /!\\** <br/> Format du code donné en entrée. <br/> Valeurs possibles: `addressed`, ~~`raw`~~ <br/> Valeur par défault: `addressed`
<br/>

**Exemple**:  

Décompile un code simple, l'absence de constant pool rend impossible l'utilisation de méthodes et de constantes.
```python
print(decompile(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x00 0x10
0x40008 0x00 0x10 0x06 0x00
"""
))
```
<br/>

Décompile un code plus complexe, la présence d'une constant pool rend possible l'utilisation de méthodes et de constantes.
```python
print(decompile(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x00 0x13
0x40008 0x01 0x00 0x00 0x00
""",
constantPool=
"""
0x0 0x0
0x1 0x01
"""
))
```
<br/>

Envois le résultat de la décompilation dans le fichier *output.txt*.
```python
decompile(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x00 0x10
0x40008 0x00 0x10 0x06 0x00
""",
outputFile="output.txt"
)
```

<br/>
<br/>
<br/>

## Interpreteur
Ce programme permet d'exécuter un binaire IJVM et renvois l'état de la pile à la fin de l'exécution.

**Fichier:** `interpreter.py`
### Utilisation:
**Fonction:** `run()`  
**Arguments:**
| Argument       | Type  | Optionelle | Description |
|:---------------|:-----:|:-----------:|:------------|
| `bytecode`     | `str` | ❌         | Code hexadécimal correspondant au code IJVM. <br/> **Doit obligatoirement être adressé.**
| `constantPool` | `str` | ✔️         | Pool de constantes hexadécimal du code IJVM. <br/> **Doit obligatoirement être adressé.**
| `outputFile`   | `str` | ✔️         | Fichier vers lequel sera envoyer le résultat.
| `format`       | `str` | ✔️         | **/!\ Non implémenté /!\\** <br/> Format du code donné en entrée. <br/> Valeurs possibles: `addressed`, ~~`raw`~~ <br/> Valeur par défault: `addressed`
<br/>

**Exemple:**

Interprète un code simple, l'absence de constant pool rend impossible l'utilisation de méthodes et de constantes.
```python
print(run(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x00 0x10
0x40008 0x00 0x10 0x06 0x00
"""
))
```
<br/>

Interprète un code plus complexe, la présence d'une constant pool rend possible l'utilisation de méthodes et de constantes.
```python
print(run(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x00 0x13
0x40008 0x01 0x00 0x00 0x00
""",
constantPool=
"""
0x0 0x0
0x1 0x01
"""
))
```
<br/>

Envois l'état de la pile dans le fichier *output.txt*.
```python
run(
"""
0x40000 0xb6 0x00 0x01 0x00
0x40004 0x01 0x00 0x00 0x10
0x40008 0x00 0x10 0x06 0x00
""",
outputFile="output.txt"
)
```
# Doll Game Launcher
VERY WIP made in about four hours. Will be going back and reworking most of it, but feel free to open issues / PRs (especially for the mods page since I lost stream around there). Next version will have an automatic update button, but this one does not lol

You can also contact me @deuil0002 on Discord


**I RECOMMEND YOU BACK UP YOUR D3DX.INI BEFORE USING THIS**, since it will reformat it and it might be a little ugly. (This will be improved on soon!)

## Planned
- Improvement of the 3DMigoto bind integration system w/ custom command lists
- Will provide an option to download GIMI and fetch a default .ini configured for Identity V
- Reorganization (seperate source from user specifications -- so eventually I can have an auto update button)
- Hash conflict manager
- Better modding / file type utils
- Integration w/ a Blender plugin

# Installation Instructions
These are instructions for Windows, since it is what most people are running Identity V on. Python is required, I am on 3.13. You can find better tutorials for installing that than I could write.

You are required to have a functional 3DMigoto. If you don't have it set up for Identity V already, I don't configure that for you, you should work on that first.

1. Clone the repository or download the .zip and extract
2. Right click while inside the folder and click "Open in Terminal"
3. Run (IN ORDER)
- `py -m venv venv`
- `Set-ExecutionPolicy Unrestricted -Scope Process`
- `venv\Scripts\activate`
- `pip install -r requirements.txt`
4. To launch, run `python main.py` (you must be in the venv!)

If you don't want to use a virtual environment, follow step 1-2 then do this instead of steps 3 and 4:

3. Run
- `py -m pip install -r requirements.txt`
4. To launch, run `py main.py`

## Setup
Before you can do anything this this launcher, you have to set up your files. Go to the Settings tab.
1. Fill in Game Executable with the path of your `dwrg.exe` (ex: mine is "C:/IdentityV2/dwrg.exe")
2. Also fill in the path of your 3DMigoto executable, and the same for the mods folder (obviously that will not be an `.exe`)
3. Click save, then 'Reload'
You should have the core functionality now. Test this by going to the home page and launching the game.

# Mod Guide
If there is no mod.json for a mod, it will be loaded by default (though you will not be able to see it in the launcher).

This is only relevant if you would like to create mods with are compatible with the launcher, or make mods work with it. I have included a script to help you. This script takes a .ini file and .jsons it for you, providing you added some parameters.

## Mod 'Types'
There are two main 'types' of mod that I have defined, 'skinmod' and ... not skinmod. It is not rocket science. A skinmod is anything that overrides an object in the game, a not skinmod is not. This means that overriding a rocket chair and a tool and a skin are skin mods, but fancy shaders are not.

Skinmods have two types under them, character and object. Character will validate the character name you provide with the character list I made; object will not. Make sure to use character if you're using a tool as well-- both Lawyer's map and Lawyer's skin mods go under his character.

## Targets
Targets are the main buffers you are targetting. You specify them above their sections. Targets are, for example, the index buffer of a skin-- not an individual texture. Don't worry, it's easier when you see it in a file.

## Preparing your .ini
Here is the .ini for a mod I created. We will be working with this to make it ready for processing. I've excluded the Resources section to make it more simple to read; you don't have to write anything new there.

```ini
; Simple weapon override mod

; default flare gun ib hash
[TextureOverrideCoordGun]
hash = b74ef525
ib = ResourceHLGunIB
vb0 = ResourceHLGunVB0
handling = skip
drawindexed = auto

[TextureOverrideFlareGunDefault]
hash = d42fe57a
this = ResourceHLGunTexture

[TextureOverrideFlareGunNormal]
hash = 1039a896
this = ResourceHLGunNormal
```

First of all, we will add some frontmatter.  You can set the id of the mod to anything you want, but try to make it unique. For the author, you put your username-- you can have multiple `; author=` lines and it will add to the authors array, not override each other.

Since we are modding a tool, it falls under `; skinmod=True`. Version is also just "put whatevery you want," it's up to you how you want to track your mod or if you will develop it more. And I think `; desc=` being the description is self-explanatory.

(Hopefully by the time you see this I will have updated the parser on the repo to allow spaces between equals signs...)

```ini
; Simple weapon override mod

; INFO FOR MOD MANAGER
; ---------------------------------------------
; id=hlglock
; author=dactyl
; skinmod=True
; version=1
; desc=Replace Coord's default gun with the original Half Life glock

; default flare gun ib hash
; ...
```

The main target of this is Coordinator's flare gun. If my file had both an outfit for her and a flare gun, I would have two targets. 

Above the section with the buffer you are noting as a target, add information about the character name, the type (it's not strict but I prefer for you to use tool or body depending on what you are doing), as well as a note so you don't rip your hair out later. 

```ini
; default flare gun ib hash
; char=coordinator type=tool note=Coord's gun ib
[TextureOverrideCoordGun]
hash = b74ef525
ib = ResourceHLGunIB
vb0 = ResourceHLGunVB0
handling = skip
drawindexed = auto
```

That's all you must do for a character skin mod. You don't have to make any non-target buffers.

### But what if I am modding an object or a shader?
For an object, simply add `; OBJECT = true` below your frontmatter. Then, instead of `; char=`, use `object=`. Type can really be whatever you wish here, but this convention seems good for me:
```ini
; object=ROCKET_CHAIR ; type=skin ; note=All above ground rocket chairs
[TextureOverrideChair]
```

While I've technically included a way to automatically do a shader, like this:
```ini
; id=my_sexy_shader
; desc=Make your PC explode
; author=dactyl
; version=1
; SHADER=true
```
I have not tested it extensively, and you may have to fill in things in your .json. Shader .jsons have not just buffer hash but for example `XXXXXX-ps` or `XXXXXX-vs`. No targets obviously.

## Turning your .ini into mod.json
Everything you did above was to prepare you to transfer your .ini into a mod.json. It is really not hard at all. We will use the `INI_PARSE.py` script at the root of this launcher.

`INI_PARSE.py` has one required parameter -- input ini. By default, it will output the mod.json in the same folder as that ini. 
```bash
> py INI_PARSE.py "C:\Users\Owner\3DMigoto\Mods\SexyMod\sexy.ini"
```
However, you can also specify an output location using the `--output_directory` argument. I don't recommend this since you will run into some errors with the loader if the .ini and mod.json are not in the same directory, but I mean if you want to you can.

```bash
> py INI_PARSE.py "C:\Users\Owner\3DMigoto\Mods\SexyMod\sexy.ini" --output_directory "C:\Users\Owner\Desktop\ModJsons"
```

By default, the launcher will look at every subdirectory in your specified Mods folder and search for mod.jsons. 

Please review your mod.json to make sure everything came out right! You can also make changes to it while the launcher is open and click "Reload" to reload everything.

[Mod Reference](https://gamebanana.com/mods/570866) that has a mod.json and nicely formatted .ini if you'd like to test your things.

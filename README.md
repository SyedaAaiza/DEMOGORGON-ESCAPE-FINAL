Demogorgan Escape
 
Technical Overview, System Architecture & Developer Documentation

An 80s retro pseudo-3D endless runner engine built with Python 3.14 and Pygame-CE. Instead of flat 2D movement, our game introduces dynamic pseudo-3D perspective scaling across 3 lanes, high-tension horror aesthetics, real-time word-hunting puzzles, character-specific telekinetic abilities, and persistent JSON profile saving.
1. Instructions for Evaluation / How to Run

Follow these simple steps to set up and launch the game on any machine:

Step 1: Clone the Repository

Open your terminal or command prompt and run:
Terminal Command: git clone https://github.com/your-username/DEMOGORGON-ESCAPE-FINAL.git
cd DEMOGORGON-ESCAPE-FINAL

Step 2: Install Required Dependencies

Make sure you have Python 3.14 (or Python 3.10+) installed. Install pygame-ce using pip:
Pip Command: pip install pygame-ce

Step 3: Run the Bootloader

To start the game, run the primary splash screen launcher script (UI/load.py):

Execution Command: python UI/load.py

Note for Evaluators: UI/load.py is the official bootloader. Running this script ensures all visual themes, audio channels, custom fonts, and high-score databases initialize cleanly before loading the Main Navigation Menu.

2. Controls & Keybindings
   
Action	Control (Keyboard)	Description

Move Left / Right	A / D or ← / → Arrow Keys	Instant 3-lane perspective slide (45px shift)

Jump	SPACEBAR or ↑ Arrow Key	Parabolic vertical jump impulse (-35px)

Double Jump	SPACEBAR (Airborne)	Second airborne jump impulse (-20px)

Crouch	S / ↓ Arrow Key / LSHIFT	Grounded crouch state box deformation

Telekinesis Ability	E	Instantiates 35 particle shards per obstacle

Pause Game	ESC Key or Click ||	Freezes game clock and displays Pause UI

4. Repository Directory Structure
```text
DEMOGORGON-ESCAPE-FINAL/
├── main.py              # Master 60 FPS Game Loop & Dynamic Scene Engine
├── WORDS.txt            # Decoupled External Word Bank
├──keys_control.py       # for backup purpose 
├── player_data.json     # Active Player Tag & Character Preference Persistence
├── highscore.json       # Local High Score Database
├── movement/            # Character Physics, Controls & Sprite Logic
│   ├── keys_control.py  # Asynchronous Keyboard Input & Lane Physics Engine
│   ├── will_move.py     # Will Byers Sprite Runner
│   ├── mike_move.py     # Mike Wheeler Sprite Runner
│   ├── el_move.py       # Eleven Sprite Runner
│   ├── dustin_move.py   # Dustin Henderson Sprite Runner
│   ├── lucas_move.py    # Lucas Sinclair Sprite Runner
│   └── max_move.py      # Max Mayfield Sprite Runner
├── UI/                  # User Interface Subsystems & Screen Modules
│   ├── load.py          # Primary Application Bootloader & Splash Screen
│   ├── menu_pg.py       # Main Menu Hub & Audio Settings (Mute / Volume)
│   ├── custom.py        # Character Selection Carousel & Name Entry Modal
│   ├── pause.py         # In-Game Pause Subsystem Overlay
│   └── game_over.py    # Game Over Subsystem & Record Saver
└── assets/              # Sprites, Fonts, Audio & Graphic Media Storage
```
5. Core Gameplay Features
   
•	Dynamic Pseudo-3D Depth Engine: 3-lane perspective Z-plane scaling running smoothly at 60 FPS without heavy GPU overhead.

•	Cognitive Word Hunt Objective: Collect track letters to spell target words (UPSIDE, VECNA, HAWKINS) to earn coin multipliers and animated HUD banners.

•	Telekinesis Ability System: Press 'E' to unleash Eleven's ability, exploding track obstacles into 35 color-fading particle shards.

•	Full Customization & Audio Control: Personalize your runner tag, select from 6 characters, and adjust audio volume or mute options in real-time.

7. Core Architecture & Team Division

•	Aaiza (Lead Systems Architect & Core Developer): Core engine loop (main.py), 3-lane physics & controls pipeline (movement/keys_control.py),will movement scripts (movement/will_move.py) pseudo-3D obstacle engine (obstacle.py), JSON database persistence, main game audio SFX curation & audio engine integration, and technical documentation.

•	Fizzah (Character Customization Architect & Visual Lead): Character selection UI layout (custom.py), Mike & Max movement scripts (movement/mike_move.py, movement/max_move.py), main game audio search & selection (finding fitting atmospheric tracks), background graphics curation, JSON database persistence ,and standalone User Guide lead.

•	Manahil (UI Layout & Sprite working): Eleven, Lucas & Dustin movement sprites , Pause Menu layout (pause.py), and secondary audio searching assistance,technical documentation assistance.

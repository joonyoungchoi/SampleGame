# SampleGame
This sample SCORE implements the game 'BLACKJACK' with customized rules

## Basic rules
  - Player can get the cards on their hand up to 5.
  - Player whose hand's value is closer to 21 than the other, will win the game. If Player whose hand's value exceeds 21, will lose. 

## Requirements

### Mint & Exchange Chips (IRC2 Token)
- 'mint_chips' method invokes the 'mint' method of chip SCORE to mint Chips.
- mint_chips: @payable, mints the amount of Chips equivalent to the value of icx (icx * 10 ** decimals)
- 'exchange' method invokes the 'burn' method of chip SCORE to burn Chips. And send icx to requestor.
- exchange: Requires the amount of icx to exchange as a input param.

### Manage Game Room
- Creation / Show list / Join / Escape & Crash
- Each gameroom has the unique ID(EOA). Gameroom ID will be derived from transaction automatically.
- Gameroom has some attributes that will be shown in a gameroom list.
    - Owner & Gameroom ID(EOA), Creation time(block height), Whether the game is active & available to join, Amount of prize per Game.
    - Prize per game : Required input param to create gameroom (default : 10 chips). Not editable after creation.
- The Creator of gameroom will be the owner of it.
- The gameroom will be crashed when the owner leaves. The owner can not leave, when the game is in active mode or the other participant exists.
- Gameroom is affordable up to 2 participants.

### Player
- Participants composed of 'owner' and 'player'.
- EOA is used for participants' ID.
- Participants' info : ready status, token balance
    - participant can toggle ready status. (True <-> False)
    - All participants' ready status muse be True to start the game.
- Participant can join only one gameroom in a same time.
- Participants able to join the gameroom or escape from it.
    - Gameroom is affordable up to 2 participants.
    - If prize per game of gameroom exceeds the chip balance of participants, then participant can not join to it.


## Game
### Game start 
- Only the owner of gameroom can start the game
- All of participants' ready status must be True.
- All participants' ready status will be set to False, when the game starts.


### Game stop
- Game will be finalized when all of pariticipants have 5 cards on their hands or decide to fix their hands.
- Game will be finalized If one of participant's value exceeds 21.
- Game is active for 30 blocks after game start time.
- Participants remain after finalizing the game. Unless the chip balance of participant is lower than prize per game.

### In-Game rules
- Players can get the cards on their hand up to 5. 
- Players can decide to fix their hand or not.
- All prize will be sent to winner. Except 'Draw'(participants will get back the chips). 

## Implementation

### SCORE
- chip : irc2 token
- samplegame : BLACKJACK

### Class 
- Samplegame : Class which contains main logic for BLACKJACK
  - Deck : Class which contains 52 cards as a list and information about deck
  - Card : Class which contains information about a card
  - Hand : Class which contains information about player's hand(card list).
  - Gameroom : Class which contains information about gameroom

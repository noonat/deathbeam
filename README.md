# Deathbeam

Deathbeam is a game I made over a tumultuous 48-hours for [Ludum Dare 14] back
in 2009. The theme for the jam was "advancing wall of doom", and my entry was
inspired by [Defender] and [Dino Run].

The game is written in Python 2.7 using [Pyglet]. I used [Tile Studio] for map.

[Ludum Dare 14]: http://ludumdare.com/
[Defender]: http://en.wikipedia.org/wiki/Defender_(arcade_game)
[Dino Run]: http://www.pixeljam.com/dinorun
[Pyglet]: http://pyglet.org/
[Tile Studio]: http://tilestudio.sourceforge.net/


# Running

To run, you'll need to install Python and the requirements. On Mac, you can do
that using [Homebrew]:

    brew install python
    git clone git@github.com:noonat/deathbeam.git
    cd deathbeam
    pip install -r requirements.txt

Then you can run the game with:

    python src/deathbeam.py

If you have performance issues, you can run it in optimized mode:

    python -OO src/deathbeam.py


# Todo

- Show civilians waiting for rescue on a pad.
- Give points when dropping civilians on a platform, and combo points if player
  drops more than one.
- Maybe add health for the player. Three hits would be death. One hit would
  give you temporary invulnerability and flash to show that you were hit.
  - Maybe lose jetpack while flashing?
  - Maybe drop civilians when hurt?
  - Could respawn at nearest spawn point when player dies?
  - Could have three deaths trigger game over?
- Add souls as a currency? Souls granted when rescuing civilians.
- Add purchasables? Could have attachments that defend you.
  - Lasers shoot bolts in a straight line, fast reload.
  - Droppable bombs, explodes on contact with world or actor, normal reload.
  - Seeking rocket, slow reload.
  - Disruptor could slow down mothership when the beam hits it.

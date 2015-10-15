# Deathbeam

![Screenshot](https://phuce.com/games/deathbeam/screenshot1.png)

**Deathbeam** is a game I made over a tumultuous 48-hours for [Ludum Dare 14]
back in 2009. The theme for the jam was "advancing wall of doom", and my entry
was inspired by [Defender] and [Dino Run].

The game is written in Python 2.7 using [Pyglet]. I used [Tile Studio] for map.

## Instructions

<table>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/mothership.png" alt="Mothership"></td>
    <td>Aliens are attacking. This is the mothership.</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/deathbeam_kill.png" alt="Deathbeam"></td>
    <td>It&apos;s charring humans left and right with its deathbeam.<br>How rude.</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/you.png" alt="You"></td>
    <td>This is you: Rescue Bot XLD-14Z. You&apos;re the humans&rsquo; only hope.</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/jetpack.png" alt="Jetpack"></td>
    <td>You can pick up humans and use your jets to carry them off to<br>safety and wellness.<br><em><strong>left &amp; right arrow</strong> to move<br><strong>space</strong> to jet</em></td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/teleport.png" alt="Teleport"></td>
    <td>Drop humans at the teleporters to beam them to safety.<br>Teleporting many at once earns you extra points!</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/civilian.png" alt="Civilian"></td>
    <td>Some humans are worth more than others. This one, however,<br>is boring. He is worth only 50 points.</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/scientist.png" alt="Scientist"></td>
    <td>This is a scientist. Scientists are worth <strong>250</strong> points.</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/mr_president.png" alt="President"></td>
    <td>This is Mr. President. The humans&rsquo; leader is worth a whopping<br><strong>1000</strong> points, robot.</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/turret_kill.png" alt="Turret"></td>
    <td>Watch out for alien turrets. Your armor protects you, but the humans<br>aren&apos;t so lucky. Poor guys.</td>
  </tr>
  <tr>
    <td><img src="https://phuce.com/games/deathbeam/rocket.png" alt="Rocket"></td>
    <td>Rescue as many humans as you can and use the rocket booster<br>to escape to orbit!</td>
  </tr>
</table>

[Ludum Dare 14]: http://ludumdare.com/
[Defender]: http://en.wikipedia.org/wiki/Defender_(arcade_game)
[Dino Run]: http://www.pixeljam.com/dinorun
[Pyglet]: http://pyglet.org/
[Tile Studio]: http://tilestudio.sourceforge.net/


## Running

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

[Homebrew]: http://brew.sh/

## Todo

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

# Programming Challenge

Welcome to the Fall 2018 WEC programming challenge! Your task is to create an AI for the
game Tron Light Cycles. The game will be played in a turn-based fashion where your AI
will send your actions to the API. Then your opponent (the AI from another participant)
will send their move into the API and the turns will continue. Their will be a round-robin
of matches to determine standing and then a knock-out tournament to determine the winner.
First in the tournament gets 50 points, second 45 and so on. Then you must make a presentation
to the panel of judges on your design. They will judge you and award up to 20 points for your 
presentation. The team with the most points at the end gets to go on to OEC!

## Tron Light Cycle Rules

Tron takes place in a 130 (horizontal) by 100 (vertical) grid. Player 1 will start at position
(33,50) facing East and Player 2 will start at position (66,50) facing West (so the two bikes
start off heading toward one another). Note that North is the direction (x,0), South is (x,100),
East is (130, x), and West is (0, x). As you and your opponent travel, a trail of light will
follow your respective bicycles. If a player collides with any trail of light, they lose. If a
player hits a wall (defined by the 130x100 grid) they lose. If the bikes collide, there is a draw
and the round is repeated. When navigating, you do so in a turn-based fashion. You declare your 
movement to the API (see below for documentation) and you have the options of moving forward one space,
turning 90 degrees (i.e. left or right) and then moving forward a space, or using a boost then moving
(same movement rules as above except when you move forward you travel 3 spaces instead of 1 (all in the
same direction: you may turn at the beginning of your turn but not after, say, moving 2 spaces)) and the
boost will last until the end of your next turn (so, each boost grants 2 turns of 3 space movement).
You get 3 boosts per round. You have 10 seconds to declare your turn (being late results in forfeiting
the round). Each match is a best of 3 rounds.

If you've never played Tron, [here is a flash version to try out](https://www.thepcmanwebsite.com/media/flash_tron/)

# Interacting With the API

### Retrieve Board Data

```
GET /grid/{game_id}/{player_id}.{format}
```

#### Parameters

<table>
  <tr>
    <td><b>Parameter</b></td>
    <td><b>Type</b></td>
    <td><b><b>Required</b></b></td>
    <td><b>Description</b></td>
  </tr>
  <tr>
    <td><b>game_id</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>id of the game of interest</td>
  </tr>
  <tr>
    <td><b>player_id</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>Your assigned unique player id</td>
  </tr>
  <tr>
    <td><b>format</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>The format of the output</td>
  </tr>
</table>

Format options: "json", "xml", OTHERS WE MAY IMPLEMENT

#### Response

<table>
  <tr>
    <td><b>Field Name</b></td>
    <td><b>Type</b></td>
    <td><b>Value Description</b></td>
  </tr>
  <tr>
  	<td><b>requester_position</b></td>
	<td>Tuple</td>
	<td>Your position on the grid</td>
  </tr>
  <tr>
  	<td><b>opponent_position</b></td>
	<td>Tuple</td>
	<td>Your position on the grid</td>
  </tr>
  <tr>
  	<td><b>grid</b></td>
	<td>Dictionary</td>
	<td>Dictionary of the grid and its contents in key-value pairs</td>
  </tr>
  <tr>
  	<td><b>player_turn</b></td>
	<td>Integer</td>
	<td>The id of whichever's player's turn it is</td>
  </tr>
</table>

#### Output
OUTPUT FROM THE ACTUAL THING WE BUILD

### Retrieve Player Data

```
GET /player/{player_number}/{game_id}/data.{format}
```

#### Parameters

<table>
  <tr>
    <td><b>Parameter</b></td>
    <td><b>Type</b></td>
    <td><b><b>Required</b></b></td>
    <td><b>Description</b></td>
  </tr>
  <tr>
    <td><b>player_number</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>The number of the player. Options: "1", "2", or a unique player id</td>
  </tr>
  <tr>
    <td><b>game_id</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>id of the game of interest</td>
  </tr>
  <tr>
    <td><b>format</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>The format of the output</td>
  </tr>
</table>

Format options: "json", "xml", OTHERS WE MAY IMPLEMENT

#### Response

<table>
  <tr>
    <td><b>Field Name</b></td>
    <td><b>Type</b></td>
    <td><b>Value Description</b></td>
  </tr>
  <tr>
  	<td><b>player_number</b></td>
	<td>Integer</td>
	<td>The number of the player (either "1" or "2")</td>
  </tr>
  <tr>
  	<td><b>player_id</b></td>
	<td>Integer</td>
	<td>The unique id of the player</td>
  </tr>
  <tr>
  	<td><b>player_position</b></td>
	<td>Tuple</td>
	<td>The position of the player on the grid</td>
  </tr>
  <tr>
  	<td><b>boost_active</b></td>
	<td>Boolean</td>
	<td>True if the player has an active boost (i.e. they used a boost last turn)</td>
  </tr>
  <tr>
  	<td><b>boosts_remaining</b></td>
	<td>Integer</td>
	<td>The number of boosts the player has remaining</td>
  </tr>
  <tr>
  	<td><b>orientation</b></td>
	<td>String</td>
	<td>The direction the player is facing (North, East, South, West)</td>
  </tr>
  <tr>
    <td><b>time_for_move</b></td>
    <td>date</td>
    <td>HH:MM:SS 24 formatted time. Time until turn expires, None if not their turn</td>
  </tr>
</table>

#### Output
OUTPUT FROM THE ACTUAL THING WE BUILD

### Move Your Cycle

```
POST /move/{game_id}/{player_id}/{turn}/{boost}/forward.{format}
```

#### Parameters

<table>
  <tr>
    <td><b>Parameter</b></td>
    <td><b>Type</b></td>
    <td><b><b>Required</b></b></td>
    <td><b>Description</b></td>
  </tr>
  <tr>
    <td><b>game_id</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>id of the game of interest</td>
  </tr>
  <tr>
    <td><b>player_id</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>Your assigned unique player id</td>
  </tr>
  <tr>
    <td><b>turn</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>Direction you want to turn this turn. Options: "Left", "Right", "None" (None for no change in direction)</td>
  </tr>
  <tr>
    <td><b>boost</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>Do you want to use a boost this turn? Options: "True", "False"</td>
  </tr>
  <tr>
    <td><b>format</b></td>
    <td>input</td>
    <td><i>yes</i></td>
    <td>The format of the output</td>
  </tr>
  <tr>
    <td><b>key</b></td>
    <td>filter</td>
    <td><i>yes</i></td>
    <td>Your API key</td>
  </tr>
</table>

#### Response

<table>
  <tr>
    <td><b>Field Name</b></td>
    <td><b>Type</b></td>
    <td><b>Value Description</b></td>
  </tr>
  <tr>
  	<td><b>requester_position</b></td>
	<td>Tuple</td>
	<td>Your position on the grid</td>
  </tr>
  <tr>
  	<td><b>grid</b></td>
	<td>Dictionary</td>
	<td>Dictionary of the grid and its contents in key-value pairs</td>
  </tr>
  <tr>
  	<td><b>player_turn</b></td>
	<td>Integer</td>
	<td>The id of whichever's player's turn it is</td>
  </tr>
  <tr>
  	<td><b>orientation</b></td>
	<td>String</td>
	<td>The direction the player is facing (North, East, South, West)</td>
  </tr>
  <tr>
    <td><b>transaction_time</b></td>
    <td>date</td>
    <td>HH:MM:SS 24 formatted time POST was received</td>
  </tr>
</table>

#### Output
OUTPUT FROM THE ACTUAL THING WE BUILD

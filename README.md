Aufhängen is a hangman game to learn German from English. You are provided a english translation of the word and have to guess the correct german word.
The game is over if you make six errors in guessing a word. The score is added +1 with every right word guessed and you can submit your final score in the
leaderboard when the game is over or you can just restart and play again.

SQL database is use to store the score submitted in a leaderboard table. The same database has a table of about 1000 german words and their translation which was scrapped from
https://1000mostcommonwords.com/1000-most-common-german-words/ as csv and imported to the table.

Flask is used as backend for this site whereas Vanilla JS is use for the frontend along HTML and CSS.

There is a main page with menu and game and a second page for leaderboard of scores.
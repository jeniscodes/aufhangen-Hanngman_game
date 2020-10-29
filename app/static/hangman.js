


let maxWrong = 6;
let mistakes = 0;
let guessed = [];
let wordStatus = null;
let hint = '';
let score = 0;


document.querySelector('#submit').disabled=true;

document.querySelector('#name').onkeyup= function(){

if (document.querySelector('#name').value.length > 0)
{

    document.querySelector('#submit').disabled=false;
}
else {
    document.querySelector('#submit').disabled=true;
}



}


document.getElementById("game").style.display='none';


document.getElementById("play").addEventListener("click", function() {


  document.getElementById("main").classList.add("game");

   document.getElementById("game").style.opacity=0;
   document.getElementById("main").style.display='none';
   document.getElementById("game").style.display='block';
   setTimeout(function () { document.getElementById("game").classList.add("gameon");
     document.getElementById("game").style.opacity=1;
   }, 1000)


});

function randomWord() {
  fetch('/word')
        .then(response=>response.json())
        .then(word=>{

                answer = `${word['german']}`;


                hint = word['english'];
                document.getElementById("hint").innerHTML= `English translation : ${hint}` ;

        });



}

function generateButtons() {
  let buttonsHTML = 'abcdefghijklmnopqrstuvwxyzäöüß'.split('').map(letter =>
    `
      <button
        class="btn btn-lg btn-dark m-2"
        id='` + letter + `'
        onClick="handleGuess('` + letter + `')"
      >
        ` + letter + `
      </button>
    `).join('');

  document.getElementById('keyboard').innerHTML = buttonsHTML;
}

function handleGuess(chosenLetter) {
  guessed.indexOf(chosenLetter) === -1 ? guessed.push(chosenLetter) : null;
  document.getElementById(chosenLetter).setAttribute('disabled', true);

  if (answer.indexOf(chosenLetter) >= 0) {
    guessedWord();
    checkIfGameWon();
  } else if (answer.indexOf(chosenLetter) === -1) {
    mistakes++;
    updateMistakes();
    checkIfGameLost();
    updateHangmanPicture();
  }
}

function updateHangmanPicture() {

  document.getElementById('hangmanPic').src = 'static/images/' + mistakes + '.jpg';
}

function checkIfGameWon() {
  if (wordStatus === answer) {
    score++;
    updateScore();
    document.getElementById('keyboard').innerHTML = 'Correct!!!';
    setTimeout(function () { randomWord();
    generateButtons();
    mistakes = 0;
    guessed = [];
    updateMistakes();
    document.getElementById('hangmanPic').src = 'static/images/0.jpg';
    setTimeout ( guessedWord, 2000);}, 1500);

  }
}

function checkIfGameLost() {
  if (mistakes === maxWrong) {
    document.getElementById('wordSpotlight').innerHTML = 'The answer was: ' + answer;
    document.getElementById('finalscore').value = score;
    document.getElementById('hidfield').value = score;
    document.getElementById('keyboard').innerHTML = `You Lost!!! <br>
    <button type="button" class="btn btn-dark" data-toggle="modal" data-target="#exampleModalCenter">
   Submit Score
</button>

<button type="button"  class="btn btn-dark" onClick="reset()">
   Play again
</button>` ;
  }

}

function guessedWord() {
  wordStatus = answer.split('').map(letter => (guessed.indexOf(letter) >= 0 ? letter : " _ ")).join('');

  document.getElementById('wordSpotlight').innerHTML = wordStatus;
}

function updateMistakes() {
  document.getElementById('mistakes').innerHTML = mistakes;
}

function updateScore() {
  document.getElementById('score').innerHTML = score;
}

function reset() {
  mistakes = 0;
  guessed = [];
  document.getElementById('hangmanPic').src = 'static/images/0.jpg';

  randomWord();
  setTimeout ( guessedWord, 2000);
  updateMistakes();
  generateButtons();
}

document.getElementById('maxWrong').innerHTML = maxWrong;

randomWord();
generateButtons();
setTimeout ( guessedWord, 2000);

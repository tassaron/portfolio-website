/* Controls top layer canvas that draws UI and captures events */
import { score, lives, percent, gameOver, gamePaused, pauseGame, swapDirection, paddle, purple, timer, startGame, canvas } from './game.js';
import { createWall } from './wall.js';
import { px2grid, grid_size } from './grid.js';

let gamediv = document.getElementById("game");
let uicanvas = document.getElementById("ui-layer");
let uictx = uicanvas.getContext("2d");
export let mouseX = 0;
export let mouseY = 0;
let prevLives = -1;
let prevScore = -1;
let prevPercent = -1;
let gameOverDrawn = false;
let livesColour = "#000";

export function addUIEventListeners() {
    /* Connect onclick events to HTML "buttons" */
    //let pause_button = document.getElementById("pause_button");
    //pause_button.addEventListener('click', pauseGame, false);
    let swap_button = document.getElementById("swap_button");
    swap_button.addEventListener('click', swapDirection, false);

    /* Connect keyboard/mouse/touch events to canvas */
    uicanvas.addEventListener("touchstart", touchStartHandler, false);
    uicanvas.addEventListener("touchend", touchEndHandler, false);
    uicanvas.addEventListener("touchmove", touchMoveHandler, false);
    uicanvas.addEventListener("mousedown", mouseDownHandler, false);
    uicanvas.addEventListener("mousemove", mouseMoveHandler, false);
    document.addEventListener("keyup", keyUpHandler, false);
}

/*
 * CONTROL HANDLERS
 */
function touchStartHandler(e) {
    touchMoveHandler(e);
    e.preventDefault();
}

function touchEndHandler(e) {
    if (gameOver == true && gamePaused == false) {
        startGame();
    } else {
        createWall()
    }
    e.preventDefault();
}

function touchMoveHandler(e) {
    // get relative (to canvas and scroll position) coords of touch
    let touch = e.changedTouches[0];
    mouseX = (touch.pageX - gamediv.offsetLeft) * uicanvas.width / uicanvas.clientWidth;
    mouseY = (touch.pageY - gamediv.offsetTop) * uicanvas.height / uicanvas.clientHeight;
    if (mouseX > 0 && mouseX < uicanvas.width) {
        paddle.x = mouseX <= grid_size ? 0 : mouseX - paddle.width / 2;
        e.preventDefault();
    }
    if (mouseY > 0 && mouseY < uicanvas.height) {
        paddle.y = mouseY <= grid_size ? 0 : mouseY - paddle.height / 2;
        e.preventDefault();
    };
}

document.getScroll = function () {
    // https://stackoverflow.com/revisions/2481776/3
    if (window.pageYOffset != undefined) {
        return [pageXOffset, pageYOffset];
    } else {
        let sx, sy, d = document,
            r = d.documentElement,
            b = d.body;
        sx = r.scrollLeft || b.scrollLeft || 0;
        sy = r.scrollTop || b.scrollTop || 0;
        return [sx, sy];
    }
}

function mouseMoveHandler(e) {
    // Get relative (to canvas and scroll position) coords of mouse
    let scroll_position = document.getScroll();
    mouseX = (e.clientX - gamediv.offsetLeft + scroll_position[0]) * uicanvas.width / uicanvas.clientWidth;
    mouseY = (e.clientY - gamediv.offsetTop + scroll_position[1]) * uicanvas.height / uicanvas.clientHeight;
    // Move paddle
    if (mouseX > 0 && mouseX < uicanvas.width) {
        paddle.x = mouseX <= grid_size ? 0 : mouseX - paddle.width / 2;
    };
    if (mouseY > 0 && mouseY < uicanvas.height) {
        paddle.y = mouseY <= grid_size ? 0 : mouseY - paddle.height / 2;
    };
}

function mouseDownHandler(e) {
    if (e.button == 0) {
        if (gameOver == true && gamePaused == false) {
            startGame();
        } else {
            createWall()
        }
    }
}


function keyUpHandler(e) {
    if (e.keyCode == 39 || e.keyCode == 37) {
        paddle.direction = 1;
    } else if (e.keyCode == 38 || e.keyCode == 40) {
        paddle.direction = 0;
    } else if (e.keyCode == 32 && gameOver == true && gamePaused == false) {
        startGame();
    } else if (e.keyCode == 80) {
        pauseGame();
    }
    e.preventDefault()
}

/*
*  DRAWING FUNCTIONS
*/

export function drawUI(force = false) {
    if (gameOver == true) {
        if (gameOverDrawn == false) {
            clearUI();
            drawGameOver();
            drawScore();
            gameOverDrawn = true;
        }
        return
    }
    if (force ||
        timer.diedRecently > 0 ||
        prevPercent != percent ||
        prevScore != score ||
        prevLives != lives ||
        timer.active == true
    ) {
        clearUI();
        drawScore();
        drawLives();
        prevPercent = percent;
        prevScore = score;
        prevLives = lives;
    };
    if (timer.ballPause > 0) {
        drawCountdown();
    } else if (timer.ballPause == 0 && timer.active == true) {
        timer.active = false;
    }
}

export function clearUI() {
    gameOverDrawn = false;
    uictx.clearRect(0, 0, uicanvas.width, uicanvas.height);
}

function drawScore() {
    uictx.font = "12pt Sans";
    uictx.fillStyle = "#000";
    uictx.fillText(`${percent}% Cleared`, grid_size, 20);
    uictx.fillText(`Score: ${score}`, grid_size * (px2grid(uicanvas.width) / 2) - 30, uicanvas.height - 10);
}

function drawLives() {
    uictx.font = "12pt Sans";
    if (timer.diedRecently > 0) {
        if (
            timer.diedRecently % 15 == 0 &&
            livesColour == "#000"
        ) {
            livesColour = "#ff0000";
        } else if (
            timer.diedRecently % 15 == 0 &&
            livesColour == "#ff0000" ||
            timer.diedRecently == 1) {
            livesColour = "#000";
        }
        timer.diedRecently--;
    }
    uictx.fillStyle = livesColour;
    if (lives == -1) {
        var livesText = "0";
    } else {
        var livesText = lives.toString();
    }
    uictx.fillText(`Lives: ${livesText}`, uicanvas.width - 72, 20);
}

function drawGameOver() {
    uictx.font = "28pt Sans";
    uictx.fillStyle = "#33aaff";
    uictx.fillText("Game Over", uicanvas.width / 2 - 102, uicanvas.height / 2 - 28);
    uictx.font = "12pt Sans";
    uictx.fillText("tap or click to restart", uicanvas.width / 2 - 86, uicanvas.height / 2 + 6);
    uictx.fillStyle = "black";
    uictx.fillText("(or play the large version", uicanvas.width / 2 - 102, uicanvas.height / 2 + 22);
    uictx.fillText("at <fun.tassaron.com/jezzball>)", uicanvas.width / 2 - 124, uicanvas.height / 2 + 42);
    //drawMuffin();
}

export function drawPauseScreen() {
    uictx.font = "28pt Sans";
    uictx.fillStyle = "#333";
    uictx.fillText("Paused", uicanvas.width / 2 - 60, uicanvas.height / 2 + 2);
}

function drawCountdown() {
    let num = Math.floor(timer.ballPause / 60) + 1;
    uictx.font = "20pt Sans";
    uictx.fillStyle = purple;
    if (num % 3 == 0) {
        uictx.fillStyle = "black";
    }
    uictx.fillText("JEZZBALL", uicanvas.width / 2 - 60, uicanvas.height / 2 - 30);
    uictx.font = "12pt Sans";
    uictx.fillText("tap/click to place a wall", uicanvas.width / 2 - 90, uicanvas.height / 2 + 30);
    uictx.fillStyle = purple;
    uictx.fillText(num, uicanvas.width / 2 - 8, uicanvas.height / 2 + 4);
}

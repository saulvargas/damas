var canvas = document.getElementById("board");

var NUM_ROWS = 8;
var NUM_COLS = 8;
var NUM_PIECES = 12;
var CELL_WHITE = 'rgb(220, 220, 220)';
var CELL_BLACK = 'rgb(100, 200, 100)';
var PIECE_BLACK = 'rgb(0, 0, 0)';
var CROSS_BLACK = 'rgb(255, 255, 255)';
var PIECE_WHITE = 'rgb(255, 255, 255)';
var CROSS_WHITE = 'rgb(0, 0, 0)';
var COLOR_SELECTED = 'rgba(100, 100, 100, 0.5)';

let CELL_HEIGHT = Math.floor(canvas.height / NUM_ROWS);
let CELL_WIDTH = Math.floor(canvas.width / NUM_COLS);
let PIECE_RADIUS = 3 / 8 * CELL_HEIGHT;
let CROWN_OUTER = 1 / 4 * CELL_HEIGHT;
let CROWN_INNER = 1 / 20 * CELL_HEIGHT;

var board = null;
window.addEventListener('resize', function() {
    CELL_HEIGHT = Math.floor(canvas.height / NUM_ROWS);
    CELL_WIDTH = Math.floor(canvas.width / NUM_COLS);
    PIECE_RADIUS = 3 / 8 * CELL_HEIGHT;
    CROWN_OUTER = 1 / 4 * CELL_HEIGHT;
    CROWN_INNER = 1 / 20 * CELL_HEIGHT;

    if (board) {
        draw(board);
    }
});

function drawBoard(ctx) {
    for (let row = 0; row < NUM_ROWS; row++) {
        var y = row * CELL_HEIGHT;
        for (let col = 0; col < NUM_COLS; col++) {
            var x = col * CELL_WIDTH;
            if (row % 2 == col % 2) {
                ctx.fillStyle = CELL_WHITE;
            } else {
                ctx.fillStyle = CELL_BLACK;
            }
            ctx.fillRect(x, y, CELL_WIDTH, CELL_HEIGHT);
        }
    }
}

function drawPiece(ctx, row, col, player) {
    var x = col * CELL_WIDTH + CELL_WIDTH / 2;
    var y = (NUM_ROWS - 1 - row) * CELL_HEIGHT + CELL_HEIGHT / 2;

    ctx.beginPath();
    ctx.arc(x, y, PIECE_RADIUS, 0, 2 * Math.PI, true);

    if (player > 0) {
        ctx.fillStyle = PIECE_WHITE;
    } else {
        ctx.fillStyle = PIECE_BLACK;
    }
    ctx.fill();

    if (Math.abs(player) > 1) {
        ctx.beginPath();

        if (player > 0) {
            ctx.fillStyle = CROSS_WHITE;
        } else {
            ctx.fillStyle = CROSS_BLACK;
        }

        ctx.fillRect(x - CROWN_OUTER / 2, y - CROWN_INNER / 2, CROWN_OUTER, CROWN_INNER);
        ctx.fillRect(x - CROWN_INNER / 2, y - CROWN_OUTER / 2, CROWN_INNER, CROWN_OUTER);
    }
}

function draw(values) {
    var ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawBoard(ctx);

    for (let row = 0; row < NUM_ROWS; row++) {
        for (let col = 0; col < NUM_COLS; col++) {
            var value = values[row][col];

            if (value != 0) {
                drawPiece(ctx, row, col, value);
            }
        }
    }
}

var webSocket = null;
var moves = null;
var posFrom = null;

canvas.onclick = function(e) {
    var ctx = canvas.getContext('2d');

    if (!moves) {
        return;
    }

    var x = e.clientX - canvas.offsetLeft;
    var y = e.clientY - canvas.offsetTop;
    var col = Math.floor(x / CELL_WIDTH);
    var row = NUM_ROWS - 1 - Math.floor(y / CELL_HEIGHT);

    x = col * CELL_WIDTH;
    y = (NUM_ROWS - 1 - row) * CELL_HEIGHT;
    ctx.fillStyle = COLOR_SELECTED;
    ctx.fillRect(x, y, CELL_WIDTH, CELL_HEIGHT);

    console.log([row, col]);

    if (!posFrom) {
        posFrom = [row, col];
    } else {
        var move = [posFrom, [row, col]];

        if (moves.map(JSON.stringify).includes(JSON.stringify(move))) {
            moves = null;
            posFrom = null;

            window.setTimeout(function() {
                webSocket.send(JSON.stringify(move));
            }, 100);
        } else {
            posFrom = null;
            draw(board);
        }

    }
}

function play(player_w, player_b) {
    webSocket = new WebSocket("ws://localhost:4444");

    var msg = {"event": "new_game", "player_w": player_w, "player_b": player_b}
    webSocket.onopen = function() {
        webSocket.send(JSON.stringify(msg))
    }

    webSocket.onmessage = function (event) {
        var msg = JSON.parse(event.data);

        if (msg.event === "render_board") {
            board = msg.board;
            draw(board);
            window.setTimeout(function() {
                webSocket.send("OK");
            }, 500);
        } else if (msg.event === "select_move") {
            moves = msg.moves;
        } else if (msg.event === "end_game") {
            var ctx = canvas.getContext('2d');
            var say;
            if (msg.winner == -1) {
                say = "GANAN NEGRAS";
            } else if (msg.winner == +1) {
                say = "GANAN BLANCAS";
            } else {
                say = "EMPATE";
            }

            ctx.font = "48px serif";
            ctx.textAlign = "center";
            ctx.fillStyle = "rgb(255, 0, 0)";
            ctx.fillText(say, canvas.width / 2, canvas.height / 2 + 16, canvas.width);
        } else {
//            console.log(msg);
        }
    }
}

var canvas = document.getElementById("board");

var NUM_ROWS = 8;
var NUM_COLS = 8;
var NUM_PIECES = 12;

var CELL_HEIGHT = 80;
var CELL_WIDTH = 80;
var PIECE_RADIUS = 30;
var CELL_WHITE = 'rgb(220, 220, 220)';
var CELL_BLACK = 'rgb(100, 200, 100)';

var PIECE_BLACK = 'rgb(0, 0, 0)';
var CROSS_BLACK = 'rgb(255, 255, 255)';
var PIECE_WHITE = 'rgb(255, 255, 255)';
var CROSS_WHITE = 'rgb(0, 0, 0)';

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

        ctx.fillRect(x - 10, y - 2, 20, 4);
        ctx.fillRect(x - 2, y - 10, 4, 20);
    }
}

function draw(values) {
    var ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, 640, 640);

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

webSocket = new WebSocket("ws://localhost:4444");

webSocket.onmessage = function (event) {
    var msg = JSON.parse(event.data);

    if (msg.event == "render_board") {
        draw(msg.board);
        window.setTimeout(function() {
            webSocket.send("OK");
        }, 500);
    } else {
        console.log(msg);
    }
}

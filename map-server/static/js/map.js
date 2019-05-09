class Node {
  constructor(pos_x, pos_y) {
    this.pos_x = pos_x;
    this.pos_y = pos_y;
  }

  update_position(pos_x, pos_y) {
    this.pos_x = pos_x;
    this.pos_y = pos_y;
  }

  show() {
    fill(52, 211, 116);
    circle(this.pos_x, this.pos_y, 10);
  }
}

let obstacles = new Array();
let robot = new Node(0,0);

function setup() {
  var canvas = createCanvas(800, windowHeight);
  canvas.parent('map-canvas');
  background(220);

  let position = io.connect('http://localhost:5000/position'); // connect to namespace position

  position.on('connect', function () {
      console.log("onconnect");

    });

  position.on('json', function (json) {
    data = JSON.parse(json);

    robot.update_position(data.pos.x, data.pos.y);
  });

  //position.emit("message", "test message");

}

function draw() {
  background(220);
  fill(0)
  textSize(20);
  text("(" + robot.pos_x.toFixed(1) + ", " + robot.pos_y.toFixed(1) + ")", 10, 30);

  robot.show();
}

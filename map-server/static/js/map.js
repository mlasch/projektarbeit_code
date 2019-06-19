class MapProperty {
  constructor(min_x, max_x, min_y, max_y) {
    this.min_x = min_x;
    this.max_x = max_x;
    this.min_y = min_y;
    this.max_y = max_y;

    this.scale = 1;
    this.offset_x = 0;
    this.offset_y = 0;

    this.width = null;
    this.height = null;
  }

  world_to_pixel(xw, yw) {
    const xp = this.scale * (-yw - this.offset_x);
    const yp = this.scale * (-xw - this.offset_y);
    return [xp, yp];
  }

  pixel_to_world(xp, yp) {
    const xw = -(yp / this.scale + this.offset_y);
    const yw = -(xp / this.scale + this.offset_x);
    return [xw, yw];
  }
}

class Checkpoint {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }

  update(x, y) {
    this.x = x;
    this.y = y;
  }

  show(p, c) {
    p.strokeWeight(mp.scale*30);
    p.stroke(100,100,100)
    p.fill(c);
    p.ellipse(this.x, this.y, mp.scale*200, mp.scale*200);
  }
}

class Arrow {
  constructor(angle) {
    this.angle = angle
    this.x1 = 0;
    this.x2 = 0;
    this.y1 = 0;
    this.y2 = 0;
  }

  update(length, pos_x, pos_y, theta) {
    this.x1 = pos_x;
    this.y1 = pos_y;

    this.x2 = pos_x + Math.cos(this.angle-theta+Math.PI)*length
    this.y2 = pos_y + Math.sin(this.angle-theta+Math.PI)*length
  }

  show(p, color) {
    p.stroke(color)
    p.strokeWeight(mp.scale*40);
    p.line(this.x1, this.y1, this.x2, this.y2);
  }
}

class Node {
  constructor(pos_x, pos_y, theta) {
    this.pos_x = pos_x;
    this.pos_y = pos_y;
    this.world_x = 0;
    this.world_y = 0;
    this.joy_x = 0;
    this.joy_y = 0;
    this.theta = theta;
    this.shape = new Polygon([new Vertex(-140, -650), new Vertex(140,-650), new Vertex(350,-500), new Vertex(350,500), new Vertex(225,800), new Vertex(-225,800), new Vertex(-350,500), new Vertex(-350,-500)]);
    this.actual = new Polygon([new Vertex(0,0)]);

    this.fb = new Arrow(Math.PI/2);
    this.lr = new Arrow(Math.PI);
  }
  update_position(pos_x, pos_y, theta, joystick) {
    this.theta = theta; // -theta+Math.PI;
    [this.pos_x, this.pos_y] = mp.world_to_pixel(pos_x, pos_y);

    this.world_x = pos_x;
    this.world_y = pos_y;

    this.joy_x = joystick.x;
    this.joy_y = joystick.y;

    // console.log(this.pos_x, this.pos_y, theta);

    //console.log(mp.scale, mp.offset_x, mp.offset_y);

    let new_polygon = new Array();
    this.shape.vertexes.forEach(function(vertex) {
      let theta = -this.theta+Math.PI;
      let x = Math.cos(theta)*vertex.x - Math.sin(theta)*vertex.y;
      let y = Math.sin(theta)*vertex.x + Math.cos(theta)*vertex.y;

      new_polygon.push(new Vertex(x + this.pos_x, y + this.pos_y));
    }, this);

    this.actual = new Polygon(new_polygon);
    //console.log("Robot: ("+this.actual.vertexes[0].x+","+this.actual.vertexes[0].y+")");

    //this.fb.update

  }

  show(p) {
    this.actual.show(p, [100, 100, 100]);
    //this.fb.show(p);
    //this.lr.show(p);
  }
}

async function getObstacles(p) {
  const response = await fetch(BASE_URL+"/floorplan");
  const data = await response.json();
  const margin = 300;

  // load all
  data.obstacles.forEach(function(polygon) {
    polygon.forEach(function(vertex) {
      const xw = vertex[0];
      const yw = vertex[1];

      const x = -yw;  // transform for pixel
      const y = -xw;

      if (x < mp.min_x) mp.min_x = x;
      if (x > mp.max_x) mp.max_x = x;
      if (y < mp.min_y) mp.min_y = y;
      if (y > mp.max_y) mp.max_y = y;
    });
  });

  // window dimensions should be fetched from the server
  console.log(mp.min_x, mp.max_x, mp.min_y, mp.max_y);

  mp.min_x = mp.min_x - margin;
  mp.max_x = mp.max_x + margin;
  mp.min_y = mp.min_y - margin*2.5;
  mp.max_y = mp.max_y + margin;

  const totalWidth = mp.max_x - mp.min_x;
  const totalHeight = mp.max_y - mp.min_y;

  if (p.windowHeight > p.windowWidth) {
    // scale to width
    mp.scale = p.windowWidth/totalWidth;
    mp.offset_x = mp.min_x;
    mp.offset_y = mp.min_y;

    mp.width = p.windowWidth;
    mp.height = totalHeight*mp.scale;
  } else {
    // scale to height
    mp.scale = p.windowHeight/totalHeight;
    mp.offset_x = mp.min_x;
    mp.offset_y = mp.min_y;

    mp.width = totalWidth*mp.scale;
    mp.height = p.windowHeight;
  }

  robot.shape.vertexes.forEach(function(v) {
    v.x = mp.scale*v.x;
    v.y = mp.scale*v.y;
  });

  data.obstacles.forEach(function(polygon) {
    const vertexes = new Array();
    polygon.forEach(function(vertex) {
      const xw = vertex[0];
      const yw = vertex[1];

      const [xp, yp] = mp.world_to_pixel(xw, yw);
      //console.log("WORLD TO PIXEL", xw, yw, xp, yp);
      vertexes.push(new Vertex(xp, yp));
    });

    obstacles.push(new Polygon(vertexes));
  });

  p.createCanvas(mp.width, mp.height);
  p.background(220);
}

async function mouseActionLeft(xp, yp) {
  const [xw, yw] = mp.pixel_to_world(xp, yp);

  cp.update(xp, yp);

  // const response = await fetch('/plan', {
  //   method: 'POST',
  //   headers: {
  //     'Content-Type': 'application/json'
  //   },
  //   body: JSON.stringify({'x': xw, 'y': yw})
  // });
  // const checkpoints = await response.json();

  // console.log(checkpoints);
}

async function mouseActionRight(xp, yp) {
  const [xw, yw] = mp.pixel_to_world(xp, yp);

  cp_list.push(new Checkpoint(xp, yp));
}

function deleteCheckpointsAction() {
  cp_list = new Array();
}

async function startCheckpointsAction() {
  const json_list = new Array();
  cp_list.forEach(function(cp_elem) {
    const [xw, yw] = mp.pixel_to_world(cp_elem.x, cp_elem.y);
    json_list.push({'x': xw, 'y': yw});
  });
  const [xw, yw] = mp.pixel_to_world(cp.x, cp.y);
  json_list.push({'x': xw, 'y': yw});

  const response = await fetch('/checkpoints', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(json_list)
  });
}

let mp  = new MapProperty(Infinity, -Infinity, Infinity, -Infinity);
let obstacles = new Array();
const robot = new Node(-100,-100,0);
const cp = new Checkpoint(-100,-100);
let cp_list = new Array();
const BASE_URL = "http://"+window.location.hostname+":5000"

let sketch = function(p) {
  p.setup = function() {

    getObstacles(p);

    let position = io.connect(BASE_URL+'/position'); // connect to namespace position

    position.on('connect', function () {
        console.log("iosocket connected");

      });

    position.on('json', function (json) {
      data = JSON.parse(json);

      robot.update_position(data.pos.x, data.pos.y, data.theta, data.joystick);
    });
    p.frameRate(30);
  }

  p.draw = function() {
    p.background(220);

    // obstacles.forEach(function(polygon) {
    //   //polygon.cspace(robot.shape).show(p, [52, 211, 116]);
    //   polygon.cspace(robot.shape).show(p, [240, 240, 240]);
    // });
    obstacles.forEach(function(polygon) {
      polygon.show(p, [184, 32, 6]);
    });

    robot.show(p);

    robot.fb.update(10+robot.joy_y*20*mp.scale, robot.pos_x, robot.pos_y, robot.theta);
    robot.fb.show(p, [255,0,0]);

    robot.lr.update(10+robot.joy_x*20*mp.scale, robot.pos_x, robot.pos_y, robot.theta);
    robot.lr.show(p, [0,255,0]);

    // draw Checkpoints
    cp.show(p, [255,0,0]);

    cp_list.forEach(function(cp_elem) {
      cp_elem.show(p, [0,255,0])
    });

    p.fill(0);
    p.stroke(0);
    p.strokeWeight(0);
    p.textSize(mp.scale*400);
    p.text("(" + robot.world_x.toFixed(1) + ", " + robot.world_y.toFixed(1) + "), Θ: "+(robot.theta/Math.PI*180).toFixed(0)+"°", mp.scale*100, mp.scale*400);
  }
  p.mouseReleased = function() {
    if (p.mouseButton === p.LEFT) {
      mouseActionLeft(p.mouseX, p.mouseY);
    }
    if (p.mouseButton === p.RIGHT) {
      mouseActionRight(p.mouseX, p.mouseY);
    }

    p.keyPressed = function() {
      if (p.keyCode === p.ESCAPE) {
        deleteCheckpointsAction();
      }

      if (p.key === 'p') {
        startCheckpointsAction();
      }
    }

  }
}

new p5(sketch, 'map-canvas');

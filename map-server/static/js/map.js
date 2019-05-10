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
  scale_x(x) {
    return mp.scale*(x-mp.offset_x);
  }
  scale_y(y) {
    return mp.scale*(y-mp.offset_y);
  }
}

class Node {
  constructor(pos_x, pos_y, theta) {
    this.pos_x = pos_x;
    this.pos_y = pos_y;
    this.theta = theta;
    this.shape = new Polygon([new Vertex(-20, -20), new Vertex(20, -20), new Vertex(20, 20), new Vertex(0,40), new Vertex(-20, 20)]);
    this.actual = new Polygon([new Vertex(0,0)]);
  }
  update_position(pos_x, pos_y, theta) {
    this.theta = theta;
    this.pos_x = mp.scale_x(pos_x);
    this.pos_y = mp.scale_y(-pos_y);

    //console.log(mp.scale, mp.offset_x, mp.offset_y);

    let new_polygon = new Array();
    this.shape.vertexes.forEach(function(vertex) {
      let x = Math.cos(this.theta)*vertex.x - Math.sin(this.theta)*vertex.y;
      let y = Math.sin(this.theta)*vertex.x + Math.cos(this.theta)*vertex.y;
      
      new_polygon.push(new Vertex(x + this.pos_x, y + this.pos_y));
    }, this);

    this.actual = new Polygon(new_polygon);
  }

  show(p) {
    this.actual.show(p, [100, 100, 100]);
  }
}

let mp  = new MapProperty(Infinity, -Infinity, Infinity, -Infinity);
let obstacles = new Array();
let robot;

let sketch = function(p) {
  p.setup = function() {
    robot = new Node(0,0,0);
    console.log(robot.actual);
    fetch("http://localhost:5000/floorplan")
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        // find window dimensions
        const margin = 300;

        data.forEach(function(polygon) {
          polygon.forEach(function(vertex) {
            let x = vertex[0];
            let y = -vertex[1];

            if (x < mp.min_x) mp.min_x = x;
            if (x > mp.max_x) mp.max_x = x;
            if (y < mp.min_y) mp.min_y = y;
            if (y > mp.max_y) mp.max_y = y;
          });
        });

        console.log(mp.min_x, mp.max_x, mp.min_y, mp.max_y);

        mp.min_x = mp.min_x - margin;
        mp.max_x = mp.max_x + margin;
        mp.min_y = mp.min_y - margin;
        mp.max_y = mp.max_y + margin;

        data.forEach(function(polygon) {
          let vertexes = new Array();
          polygon.forEach(function(vertex) {
            let x = vertex[0];
            let y = -vertex[1];

            //if ((mp.max_y - mp.min_y) > (mp.max_x - mp.min_x)) {
            if (p.windowHeight > p.windowWidth) {
              // scale to width
              mp.scale = p.windowWidth/(mp.max_x-mp.min_x);
              mp.offset_x = mp.min_x;
              mp.offset_y = mp.min_y;

              mp.width = p.windowWidth;
              mp.height = (mp.max_y-mp.min_y)*mp.scale;
            } else {
              // scale to height
              mp.scale = p.windowHeight/(mp.max_y-mp.min_y);
              mp.offset_x = mp.min_x;
              mp.offset_y = mp.min_y;

              mp.width = (mp.max_x-mp.min_x)*mp.scale;
              mp.height = p.windowHeight;
            }

            //console.log("x: " + 1000 + " to " + mp.scale_x(1000));
            //console.log("y: " + -y + " to " + mp.scale_y(y));

            vertexes.push(new Vertex(mp.scale_x(x), mp.scale_y(y)));
          });

          obstacles.push(new Polygon(vertexes));
        });
        // console.log(mp.min_x, mp.max_x, mp.min_y, mp.max_y);
        // console.log(mp.scale, mp.offset_x, mp.offset_y);
        // console.log(mp.width, mp.height);

        p.createCanvas(mp.width, mp.height);
        p.background(220);
      });

    let position = io.connect('http://localhost:5000/position'); // connect to namespace position

    position.on('connect', function () {
        console.log("onconnect");

      });

    position.on('json', function (json) {
      data = JSON.parse(json);

      robot.update_position(data.pos.x, data.pos.y, data.theta);
    });

    //position.emit("message", "test message");
    p.frameRate(30);
  }

  p.draw = function() {
    p.background(220);

    obstacles.forEach(function(polygon) {
      polygon.cspace(robot.shape).show(p, [52, 211, 116]);
    });
    obstacles.forEach(function(polygon) {
      polygon.show(p, [244, 92, 66]);
    });

    robot.show(p);

    p.fill(0);
    p.textSize(20);
    p.text("(" + robot.pos_x.toFixed(1) + ", " + robot.pos_y.toFixed(1) + ")", 10, 30);

    //p.translate(100,100);
    //robot.shape.show(p, [0,0,0]);
    //p.translate(0,0);
  }
}

new p5(sketch, 'map-canvas');

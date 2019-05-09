class Vertex {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }
  subtract(other) {
    return new Vertex(this.x - other.x, this.y - other.y)
  }
}

class Polygon {
  constructor(vertexes) {
    this.vertexes = vertexes;
  }

  show(p, color) {
    p.fill(color);  // fill color
    p.strokeWeight(0);  // no border
    p.beginShape();
    this.vertexes.forEach(function(v) {
      p.vertex(v.x, v.y);

    });
    p.endShape(p.CLOSE);
  }

  show_vertexes(p, color) {
    this.vertexes.forEach(function(v) {
      p.strokeWeight(0);
      p.fill(color);
      p.circle(v.x, v.y, 10);
    });
  }

  move(x, y) {
    this.x = this.x + x;
    this.y = this.y + y;
  }

  cspace(other) {
    // S: Set of points resulting from the Minkowsky sum
    let S = new Array();
    other.vertexes.forEach(function(v1) {
      this.vertexes.forEach(function(v2) {
        S.push(new Vertex(v1.x + v2.x, v1.y + v2.y));
      });
    }, this);

    // gift wrapping algorithm
    S.sort(function(a, b) {
      if (a.x < b.x) {
        return -1;
      }
      if (a.x > b.x) {
        return 1;
      }
      return 0; //a and b are equal
    });

    let P = new Array();
    let start_p = S[0];  //point on the hull
    let next_p;

    do {
      //console.log("found new vertex: " + start_p.x + ", " + start_p.y);
      P.push(start_p);
      next_p = null;

      // find a point with the greatest left turn
      S.forEach(function(check_p) {
        if (next_p == null) {
          next_p = check_p;
        } else {
          let position = (next_p.x - start_p.x) * (check_p.y - start_p.y) - (next_p.y - start_p.y) * (check_p.x - start_p.x)

          if (start_p == next_p || position < 0) {
            //found greater left turn
            next_p = check_p;
          }
        }
      });

      start_p = next_p;

    } while (next_p != P[0]);  // unitl ==

    return new Polygon(P);
  }
}

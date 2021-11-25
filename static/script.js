init()

function init() {
    // TableDrawBlank(20, 20);                  // draw table
    Test(5, 5);
}

function Test(col, row){
  var tbl = document.getElementById('id_game_table').getElementsByTagName('tbody')[0];
;
//  tbl.style.height = (row * 20) + 'px';
//  tbl.style.width = (col * 20) + 'px';
//  tbl.style.border = '1px solid black';

//  var cell = row.insertCell(0);
//
//    th = tbl.insertThead();
//    row = th.insertRow(0);
//    for (let j = 0; j < col; j++) {
//        cell = row.insertCell(0);
//        cell.classList = "tdicon";
//    }

  for (let i = 0; i < row; i++) {
    tr = tbl.insertRow(i);
    for (let j = 0; j < col; j++) {
        td = tr.insertCell();
        td.classList = 'green-cell';

        if (i === 1 && j === 1) {
            img = document.createElement("img");
            img.src = "static/favicon.ico";
            img.style.height = '30px';
            img.style.width = '30px';
            td.appendChild(img);
        }
        td.style.border = '1px solid black';
    }
  }
}


function TableDrawBlank(col, row) {
    let table = document.getElementById('game_table');

    // удаляем таблицу
    // TableDrop();
    // TODO сделать нормальную генерацию, а не вставлять в позицию 0.
    // генерируем заново
    for (var i = row - 1; i >= 0; i--) {
        let x = table.insertRow(0);
        for (var j=0; j < col; j++) {
            table.rows[0].insertCell(j);
            table.rows[0].cells[j].id = 'td' + i + '_' + j
            table.rows[0].cells[j].classList = 'cell living-cell';
            // table.rows[0].cells[j].style.cssText = 'width: 1%';
        }
    }
    alert("I am an alert box!");
}
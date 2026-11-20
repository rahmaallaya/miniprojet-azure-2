const A = '/api/instruments';
const $ = i => document.getElementById(i);
let D = [], editId = null;

async function charger() {
  D = await (await fetch(A)).json();
  $('t').innerHTML = D.map(x => '<tr><td>' + x.nom + '</td><td>' + x.description +
    '</td><td>' + x.prix.toFixed(2) + ' DT</td><td>' + x.categorie +
    '</td><td><button class="btn btn-warning btn-sm" onclick="edit(' + x.id + ')">Modifier</button> ' +
    '<button class="btn btn-danger btn-sm" onclick="del(' + x.id + ')">Supprimer</button></td></tr>').join('');
}

function edit(id) {
  const x = D.find(d => d.id === id);
  ['nom','description','prix','categorie'].forEach(k => $(k).value = x[k]);
  editId = id;
}

async function del(id) {
  if (!confirm('Supprimer cet instrument ?')) return;
  await fetch(A + '/' + id, {method: 'DELETE'});
  charger();
}

$('f').onsubmit = async e => {
  e.preventDefault();
  const body = JSON.stringify({nom: $('nom').value, description: $('description').value,
    prix: parseFloat($('prix').value), categorie: $('categorie').value});
  await fetch(editId ? A + '/' + editId : A, {method: editId ? 'PUT' : 'POST',
    headers: {'Content-Type': 'application/json'}, body: body});
  editId = null; $('f').reset(); charger();
};

charger();

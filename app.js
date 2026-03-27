async function loadRaces() {
  const res = await fetch('data/upcoming_races.json');
  const races = await res.json();

  const container = document.getElementById('races');
  container.innerHTML = '';

  races.forEach(race => {
    const div = document.createElement('div');
    div.className = 'race';

    const title = document.createElement('h3');
    title.innerText = race.time + ' ' + race.course;
    div.appendChild(title);

    race.runners.sort((a,b) => b.implied_prob - a.implied_prob);

    race.runners.forEach((r, index) => {
      const row = document.createElement('div');
      row.className = 'horse';
      if(index === 0) row.classList.add('top');
      row.innerHTML = `<span>${index+1}. ${r.horse}</span><span>${(r.implied_prob*100).toFixed(1)}%</span>`;
      div.appendChild(row);
    });

    container.appendChild(div);
  });
}

loadRaces();
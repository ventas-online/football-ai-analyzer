const demoPredictions = [
  {match:'Demo FC vs Demo United', market:'Over 2.5', probability:0.68, confidence:'MEDIA'},
  {match:'Demo City vs Demo Athletic', market:'1X', probability:0.74, confidence:'MEDIA'}
];

function renderDemo() {
  const root = document.querySelector('#signals');
  if (!root) return;
  root.innerHTML = demoPredictions.map(x => `
    <div class="signal">
      <div><strong>${x.match}</strong><small>${x.market}</small></div>
      <div class="prob">${(x.probability * 100).toFixed(0)}%</div>
      <span>${x.confidence}</span>
    </div>`).join('');
}

document.addEventListener('DOMContentLoaded', renderDemo);

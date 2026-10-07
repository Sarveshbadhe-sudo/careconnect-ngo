// Dynamic Impact calculation: Rs 25 = 1 meal
function updateImpact(amount) {
    const meals = Math.floor(amount / 25);
    const counter = document.getElementById('impactCounter');
    if (counter) {
        counter.innerText = `You will fund ${meals.toLocaleString()} warm meals`;
    }
}

function setAmount(val) {
    const customInput = document.getElementById('customAmount');
    if (customInput) {
        customInput.value = val;
        updateImpact(val);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const customInput = document.getElementById('customAmount');
    if (customInput) {
        customInput.addEventListener('input', (e) => {
            updateImpact(e.target.value || 0);
        });
    }
});
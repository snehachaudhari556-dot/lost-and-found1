// 1. Sidebar Navigation Logic
document.querySelectorAll('#main-nav li').forEach(item => {
    item.addEventListener('click', () => {
        // Switch Active Class in Sidebar
        document.querySelectorAll('#main-nav li').forEach(el => el.classList.remove('active'));
        item.classList.add('active');

        // Switch Visible Page
        const target = item.getAttribute('data-target');
        document.querySelectorAll('.page-view').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(target).classList.add('active');
    });
});

// 2. Button Navigation (Helper for Dashboard buttons)
function switchTo(pageId) {
    document.querySelector(`[data-target="${pageId}"]`).click();
}

// 3. Lost Report: Toggle Person/Item fields
function setLostType(type) {
    const extras = document.getElementById('person-extras');
    const label = document.getElementById('name-label');
    const buttons = document.querySelectorAll('.toggle-btn');

    // Update buttons
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    if(type === 'person') {
        extras.style.display = 'block';
        label.innerText = "Person's Name:";
    } else {
        extras.style.display = 'none';
        label.innerText = "Item Name:";
    }
}
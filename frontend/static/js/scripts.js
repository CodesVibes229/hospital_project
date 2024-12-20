document.addEventListener("DOMContentLoaded", function () {
    fetch('/api/hospitals')
        .then(response => response.json())
        .then(data => {
            const hospitalList = document.getElementById('hospital-list');
            data.forEach(hospital => {
                const div = document.createElement('div');
                div.innerHTML = `
                    <h3>${hospital.name}</h3>
                    <p>Adresse: ${hospital.address}</p>
                    <p>Téléphone: ${hospital.phone}</p>
                    <p>Disponibilité: ${hospital.availability}</p>
                    <p>Services: ${hospital.services}</p>
                    <hr>
                `;
                hospitalList.appendChild(div);
            });
        })
        .catch(err => console.error('Erreur lors de la récupération des hôpitaux:', err));
});
function deleteReservation(id) {
    if (confirm("Are you sure you want to delete this reservation?")) {
        fetch('/admin/reservations/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: id })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            location.reload(); // Перезагрузка страницы после удаления
        })
        .catch(error => console.error('Error:', error));
    }
}

function editReservation(id, customer_name, phone, reservation_date, table_number) {
    const newName = prompt("Enter new customer name:", customer_name);
    const newPhone = prompt("Enter new phone number:", phone);
    const newDate = prompt("Enter new reservation date (YYYY-MM-DD HH:MM:SS):", reservation_date);
    const newTable = prompt("Enter new table number:", table_number);

    if (newName && newPhone && newDate && newTable) {
        fetch('/admin/reservations/edit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: id,
                customer_name: newName,
                phone: newPhone,
                reservation_date: newDate,
                table_number: newTable
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            location.reload(); // Перезагрузка страницы после обновления
        })
        .catch(error => console.error('Error:', error));
    }
}
